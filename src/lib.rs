//! # RustMatch - High-Performance Template Matching Library
//!
//! A Python library for fast template matching using Normalized Cross-Correlation (NCC).
//! 
//! ## Zero Dependencies Mode
//! 
//! This library can work without numpy by using file paths or bytes directly.
//! The image crate handles all image loading and conversion internally.

use image::{DynamicImage, GrayImage, GenericImageView};
use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyIOError};
use pyo3::types::PyBytes;
use rayon::prelude::*;
use std::io::Cursor;

// ============================================================================
// Data Structures
// ============================================================================

/// Match result containing position and confidence score
#[pyclass]
#[derive(Clone)]
pub struct MatchResult {
    #[pyo3(get)]
    pub x: u32,
    #[pyo3(get)]
    pub y: u32,
    #[pyo3(get)]
    pub confidence: f64,
}

#[pymethods]
impl MatchResult {
    fn __repr__(&self) -> String {
        format!("MatchResult(x={}, y={}, confidence={:.4})", self.x, self.y, self.confidence)
    }
    
    fn __str__(&self) -> String {
        self.__repr__()
    }
    
    fn to_tuple(&self) -> (u32, u32, f64) {
        (self.x, self.y, self.confidence)
    }
    
    fn bbox(&self, width: u32, height: u32) -> (u32, u32, u32, u32) {
        (self.x, self.y, width, height)
    }
}

/// Internal grayscale image wrapper
struct GrayImageData {
    data: Vec<f64>,
    width: usize,
    height: usize,
}

impl GrayImageData {
    fn from_gray_image(img: &GrayImage) -> Self {
        let (w, h) = img.dimensions();
        let data: Vec<f64> = img.as_raw().iter().map(|&v| v as f64).collect();
        Self { data, width: w as usize, height: h as usize }
    }
    
    fn from_dynamic(img: &DynamicImage) -> Self {
        Self::from_gray_image(&img.to_luma8())
    }
}

// ============================================================================
// Integral Image Implementation
// ============================================================================

struct IntegralImage {
    sum: Vec<f64>,
    sq_sum: Vec<f64>,
    width: usize,
}

impl IntegralImage {
    fn new(data: &[f64], w: usize, h: usize) -> Self {
        let width = w + 1;
        let size = width * (h + 1);
        
        let mut sum = vec![0.0f64; size];
        let mut sq_sum = vec![0.0f64; size];

        for y in 0..h {
            let row_offset = y * w;
            for x in 0..w {
                let v = data[row_offset + x];
                let idx = (y + 1) * width + (x + 1);
                let idx_up = y * width + (x + 1);
                let idx_left = (y + 1) * width + x;
                let idx_diag = y * width + x;
                
                sum[idx] = v + sum[idx_up] + sum[idx_left] - sum[idx_diag];
                sq_sum[idx] = v * v + sq_sum[idx_up] + sq_sum[idx_left] - sq_sum[idx_diag];
            }
        }
        Self { sum, sq_sum, width }
    }

    #[inline(always)]
    fn get_stats(&self, x: usize, y: usize, w: usize, h: usize) -> (f64, f64) {
        let idx1 = y * self.width + x;
        let idx2 = y * self.width + (x + w);
        let idx3 = (y + h) * self.width + x;
        let idx4 = (y + h) * self.width + (x + w);
        
        unsafe {
            let s = *self.sum.get_unchecked(idx4) - *self.sum.get_unchecked(idx2) 
                  - *self.sum.get_unchecked(idx3) + *self.sum.get_unchecked(idx1);
            let sq = *self.sq_sum.get_unchecked(idx4) - *self.sq_sum.get_unchecked(idx2) 
                   - *self.sq_sum.get_unchecked(idx3) + *self.sq_sum.get_unchecked(idx1);
            (s, sq)
        }
    }
}

// ============================================================================
// Template Preprocessing
// ============================================================================

struct Template {
    normalized: Vec<f64>,
    width: usize,
    height: usize,
    inv_std_n: f64,
}

impl Template {
    fn new(data: &[f64], w: usize, h: usize) -> Self {
        let n = (w * h) as f64;
        let sum: f64 = data.iter().sum();
        let sq_sum: f64 = data.iter().map(|&v| v * v).sum();
        let mean = sum / n;
        let var = (sq_sum / n) - mean * mean;
        let std = var.sqrt().max(1e-10);
        let normalized: Vec<f64> = data.iter().map(|&v| v - mean).collect();
        Self { normalized, width: w, height: h, inv_std_n: 1.0 / (std * n) }
    }
}

// ============================================================================
// NCC Core Computation
// ============================================================================

#[inline(always)]
fn compute_ncc(
    src: &[f64], src_width: usize, integral: &IntegralImage, tpl: &Template, x: usize, y: usize,
) -> f64 {
    let tw = tpl.width;
    let th = tpl.height;
    let n = (tw * th) as f64;

    let (s_sum, s_sq_sum) = integral.get_stats(x, y, tw, th);
    let s_mean = s_sum / n;
    let s_var = (s_sq_sum / n) - s_mean * s_mean;
    
    if s_var < 1.0 { return 0.0; }
    let s_std = s_var.sqrt();

    let mut cross = 0.0f64;
    let mut tpl_idx = 0;
    
    for ty in 0..th {
        let src_row = (y + ty) * src_width + x;
        for tx in 0..tw {
            let sv = unsafe { *src.get_unchecked(src_row + tx) } - s_mean;
            let tv = unsafe { *tpl.normalized.get_unchecked(tpl_idx) };
            cross += sv * tv;
            tpl_idx += 1;
        }
    }
    cross * tpl.inv_std_n / s_std
}

// ============================================================================
// Search Strategies
// ============================================================================

fn search_best(src: &[f64], sw: usize, sh: usize, tpl: &Template, threshold: f64) -> Option<MatchResult> {
    let tw = tpl.width;
    let th = tpl.height;
    if tw > sw || th > sh { return None; }

    let integral = IntegralImage::new(src, sw, sh);
    let end_x = sw - tw;
    let end_y = sh - th;

    let best = (0..=end_y)
        .into_par_iter()
        .map(|y| {
            let mut row_best = (0usize, y, -1.0f64);
            for x in 0..=end_x {
                let score = compute_ncc(src, sw, &integral, tpl, x, y);
                if score > row_best.2 { row_best = (x, y, score); }
            }
            row_best
        })
        .reduce(|| (0, 0, -1.0f64), |a, b| if a.2 > b.2 { a } else { b });

    if best.2 >= threshold {
        Some(MatchResult { x: best.0 as u32, y: best.1 as u32, confidence: best.2 })
    } else { None }
}

fn search_region(
    src: &[f64], sw: usize, sh: usize, tpl: &Template,
    x1: usize, y1: usize, x2: usize, y2: usize, threshold: f64,
) -> Option<MatchResult> {
    let integral = IntegralImage::new(src, sw, sh);
    let mut best = (0usize, 0usize, -1.0f64);
    
    for y in y1..=y2 {
        for x in x1..=x2 {
            let score = compute_ncc(src, sw, &integral, tpl, x, y);
            if score > best.2 { best = (x, y, score); }
        }
    }

    if best.2 >= threshold {
        Some(MatchResult { x: best.0 as u32, y: best.1 as u32, confidence: best.2 })
    } else { None }
}

fn downsample(src: &[f64], sw: usize, sh: usize, scale: usize) -> (Vec<f64>, usize, usize) {
    let nw = sw / scale;
    let nh = sh / scale;
    let mut result = vec![0.0; nw * nh];
    let scale_sq = (scale * scale) as f64;
    
    for y in 0..nh {
        for x in 0..nw {
            let mut sum = 0.0;
            for dy in 0..scale {
                for dx in 0..scale {
                    sum += src[(y * scale + dy) * sw + (x * scale + dx)];
                }
            }
            result[y * nw + x] = sum / scale_sq;
        }
    }
    (result, nw, nh)
}

fn pyramid_match(
    src: &[f64], sw: usize, sh: usize, tpl_data: &[f64], tw: usize, th: usize, threshold: f64,
) -> Option<MatchResult> {
    if tw > sw || th > sh { return None; }

    let min_tpl_size = 16usize;
    let max_scale = tw.min(th) / min_tpl_size;
    let scale = max_scale.min(8).next_power_of_two().max(1);

    if scale >= 4 {
        let (small_src, ssw, ssh) = downsample(src, sw, sh, scale);
        let (small_tpl, stw, sth) = downsample(tpl_data, tw, th, scale);
        let small_template = Template::new(&small_tpl, stw, sth);
        
        if let Some(coarse) = search_best(&small_src, ssw, ssh, &small_template, threshold * 0.5) {
            let margin = scale * 4;
            let cx = coarse.x as usize * scale;
            let cy = coarse.y as usize * scale;
            
            let x1 = cx.saturating_sub(margin);
            let y1 = cy.saturating_sub(margin);
            let x2 = (cx + margin).min(sw.saturating_sub(tw));
            let y2 = (cy + margin).min(sh.saturating_sub(th));
            
            let tpl = Template::new(tpl_data, tw, th);
            return search_region(src, sw, sh, &tpl, x1, y1, x2, y2, threshold);
        }
        None
    } else {
        let tpl = Template::new(tpl_data, tw, th);
        search_best(src, sw, sh, &tpl, threshold)
    }
}

fn match_multi(
    src: &[f64], sw: usize, sh: usize, tpl_data: &[f64], tw: usize, th: usize,
    threshold: f64, max_count: usize,
) -> Vec<MatchResult> {
    if tw > sw || th > sh { return vec![]; }

    let integral = IntegralImage::new(src, sw, sh);
    let tpl = Template::new(tpl_data, tw, th);
    let end_x = sw - tw;
    let end_y = sh - th;
    let step = 2usize;
    
    let candidates: Vec<_> = (0..=end_y / step)
        .into_par_iter()
        .flat_map(|yi| {
            let y = yi * step;
            let mut row_candidates = Vec::new();
            for xi in 0..=end_x / step {
                let x = xi * step;
                let score = compute_ncc(src, sw, &integral, &tpl, x, y);
                if score >= threshold * 0.9 { row_candidates.push((x, y, score)); }
            }
            row_candidates
        })
        .collect();

    let mut results: Vec<MatchResult> = candidates
        .iter()
        .filter_map(|&(cx, cy, _)| {
            let mut best = (cx, cy, -1.0f64);
            for dy in 0..step {
                for dx in 0..step {
                    let x = (cx + dx).min(end_x);
                    let y = (cy + dy).min(end_y);
                    let score = compute_ncc(src, sw, &integral, &tpl, x, y);
                    if score > best.2 { best = (x, y, score); }
                }
            }
            if best.2 >= threshold {
                Some(MatchResult { x: best.0 as u32, y: best.1 as u32, confidence: best.2 })
            } else { None }
        })
        .collect();

    results.sort_by(|a, b| b.confidence.partial_cmp(&a.confidence).unwrap());
    
    let mut filtered = Vec::new();
    for r in results {
        let overlaps = filtered.iter().any(|f: &MatchResult| {
            let dx = (r.x as i32 - f.x as i32).abs() as u32;
            let dy = (r.y as i32 - f.y as i32).abs() as u32;
            dx < tw as u32 / 2 && dy < th as u32 / 2
        });
        if !overlaps {
            filtered.push(r);
            if filtered.len() >= max_count { break; }
        }
    }
    filtered
}

// ============================================================================
// Image Loading Helpers
// ============================================================================

fn load_image_from_path(path: &str) -> PyResult<GrayImageData> {
    let img = image::open(path)
        .map_err(|e| PyIOError::new_err(format!("Failed to load image '{}': {}", path, e)))?;
    Ok(GrayImageData::from_dynamic(&img))
}

fn load_image_from_bytes(data: &[u8]) -> PyResult<GrayImageData> {
    let img = image::load_from_memory(data)
        .map_err(|e| PyValueError::new_err(format!("Failed to decode image: {}", e)))?;
    Ok(GrayImageData::from_dynamic(&img))
}

// ============================================================================
// Python Interface - File Path Based (No numpy needed!)
// ============================================================================

/// Find single best match using file paths
/// 
/// Args:
///     source_path: Path to source image file
///     template_path: Path to template image file
///     threshold: Matching threshold (0.0-1.0), default 0.8
/// 
/// Returns:
///     MatchResult or None
#[pyfunction]
#[pyo3(signature = (source_path, template_path, threshold=0.8))]
fn find_template(
    source_path: &str,
    template_path: &str,
    threshold: f64,
) -> PyResult<Option<MatchResult>> {
    let src = load_image_from_path(source_path)?;
    let tpl = load_image_from_path(template_path)?;
    
    Ok(pyramid_match(
        &src.data, src.width, src.height,
        &tpl.data, tpl.width, tpl.height,
        threshold
    ))
}

/// Find all matches using file paths
/// 
/// Args:
///     source_path: Path to source image file
///     template_path: Path to template image file
///     threshold: Matching threshold (0.0-1.0), default 0.8
///     max_count: Maximum number of matches, default 10
/// 
/// Returns:
///     List of MatchResult objects
#[pyfunction]
#[pyo3(signature = (source_path, template_path, threshold=0.8, max_count=10))]
fn find_all_templates(
    source_path: &str,
    template_path: &str,
    threshold: f64,
    max_count: usize,
) -> PyResult<Vec<MatchResult>> {
    let src = load_image_from_path(source_path)?;
    let tpl = load_image_from_path(template_path)?;
    
    Ok(match_multi(
        &src.data, src.width, src.height,
        &tpl.data, tpl.width, tpl.height,
        threshold, max_count
    ))
}

// ============================================================================
// Python Interface - Bytes Based (No numpy needed!)
// ============================================================================

/// Find single best match using image bytes
/// 
/// Args:
///     source_bytes: Source image as bytes (PNG, JPEG, etc.)
///     template_bytes: Template image as bytes
///     threshold: Matching threshold (0.0-1.0), default 0.8
/// 
/// Returns:
///     MatchResult or None
#[pyfunction]
#[pyo3(signature = (source_bytes, template_bytes, threshold=0.8))]
fn find_template_bytes(
    source_bytes: &[u8],
    template_bytes: &[u8],
    threshold: f64,
) -> PyResult<Option<MatchResult>> {
    let src = load_image_from_bytes(source_bytes)?;
    let tpl = load_image_from_bytes(template_bytes)?;
    
    Ok(pyramid_match(
        &src.data, src.width, src.height,
        &tpl.data, tpl.width, tpl.height,
        threshold
    ))
}

/// Find all matches using image bytes
/// 
/// Args:
///     source_bytes: Source image as bytes (PNG, JPEG, etc.)
///     template_bytes: Template image as bytes
///     threshold: Matching threshold (0.0-1.0), default 0.8
///     max_count: Maximum number of matches, default 10
/// 
/// Returns:
///     List of MatchResult objects
#[pyfunction]
#[pyo3(signature = (source_bytes, template_bytes, threshold=0.8, max_count=10))]
fn find_all_templates_bytes(
    source_bytes: &[u8],
    template_bytes: &[u8],
    threshold: f64,
    max_count: usize,
) -> PyResult<Vec<MatchResult>> {
    let src = load_image_from_bytes(source_bytes)?;
    let tpl = load_image_from_bytes(template_bytes)?;
    
    Ok(match_multi(
        &src.data, src.width, src.height,
        &tpl.data, tpl.width, tpl.height,
        threshold, max_count
    ))
}

// ============================================================================
// Python Interface - Raw Pixel Data (List of integers, no numpy!)
// ============================================================================

/// Find single best match using raw pixel data as flat list
/// 
/// Args:
///     source_pixels: Source image pixels as flat list of integers (0-255)
///     source_width: Source image width
///     source_height: Source image height
///     template_pixels: Template pixels as flat list of integers (0-255)
///     template_width: Template width
///     template_height: Template height
///     threshold: Matching threshold (0.0-1.0), default 0.8
/// 
/// Returns:
///     MatchResult or None
#[pyfunction]
#[pyo3(signature = (source_pixels, source_width, source_height, template_pixels, template_width, template_height, threshold=0.8))]
fn find_template_raw(
    source_pixels: Vec<u8>,
    source_width: usize,
    source_height: usize,
    template_pixels: Vec<u8>,
    template_width: usize,
    template_height: usize,
    threshold: f64,
) -> PyResult<Option<MatchResult>> {
    if source_pixels.len() != source_width * source_height {
        return Err(PyValueError::new_err("Source pixel count doesn't match dimensions"));
    }
    if template_pixels.len() != template_width * template_height {
        return Err(PyValueError::new_err("Template pixel count doesn't match dimensions"));
    }
    
    let src: Vec<f64> = source_pixels.iter().map(|&v| v as f64).collect();
    let tpl: Vec<f64> = template_pixels.iter().map(|&v| v as f64).collect();
    
    Ok(pyramid_match(&src, source_width, source_height, &tpl, template_width, template_height, threshold))
}

/// Find all matches using raw pixel data as flat list
#[pyfunction]
#[pyo3(signature = (source_pixels, source_width, source_height, template_pixels, template_width, template_height, threshold=0.8, max_count=10))]
fn find_all_templates_raw(
    source_pixels: Vec<u8>,
    source_width: usize,
    source_height: usize,
    template_pixels: Vec<u8>,
    template_width: usize,
    template_height: usize,
    threshold: f64,
    max_count: usize,
) -> PyResult<Vec<MatchResult>> {
    if source_pixels.len() != source_width * source_height {
        return Err(PyValueError::new_err("Source pixel count doesn't match dimensions"));
    }
    if template_pixels.len() != template_width * template_height {
        return Err(PyValueError::new_err("Template pixel count doesn't match dimensions"));
    }
    
    let src: Vec<f64> = source_pixels.iter().map(|&v| v as f64).collect();
    let tpl: Vec<f64> = template_pixels.iter().map(|&v| v as f64).collect();
    
    Ok(match_multi(&src, source_width, source_height, &tpl, template_width, template_height, threshold, max_count))
}

// ============================================================================
// Utility Functions
// ============================================================================

/// Get image dimensions from file path
/// 
/// Returns:
///     Tuple of (width, height)
#[pyfunction]
fn get_image_size(path: &str) -> PyResult<(u32, u32)> {
    let img = image::open(path)
        .map_err(|e| PyIOError::new_err(format!("Failed to load image: {}", e)))?;
    Ok(img.dimensions())
}

/// Get image dimensions from bytes
#[pyfunction]
fn get_image_size_bytes(data: &[u8]) -> PyResult<(u32, u32)> {
    let img = image::load_from_memory(data)
        .map_err(|e| PyValueError::new_err(format!("Failed to decode image: {}", e)))?;
    Ok(img.dimensions())
}

/// Set number of threads for parallel processing
#[pyfunction]
fn set_num_threads(num_threads: usize) -> PyResult<()> {
    rayon::ThreadPoolBuilder::new()
        .num_threads(if num_threads == 0 { num_cpus::get() } else { num_threads })
        .build_global()
        .map_err(|e| PyValueError::new_err(format!("Failed to set threads: {}", e)))
}

/// Get library version
#[pyfunction]
fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

// ============================================================================
// Module Definition
// ============================================================================

#[pymodule]
fn _core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MatchResult>()?;
    
    // File path based (recommended, no numpy!)
    m.add_function(wrap_pyfunction!(find_template, m)?)?;
    m.add_function(wrap_pyfunction!(find_all_templates, m)?)?;
    
    // Bytes based (no numpy!)
    m.add_function(wrap_pyfunction!(find_template_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(find_all_templates_bytes, m)?)?;
    
    // Raw pixel data (no numpy!)
    m.add_function(wrap_pyfunction!(find_template_raw, m)?)?;
    m.add_function(wrap_pyfunction!(find_all_templates_raw, m)?)?;
    
    // Utilities
    m.add_function(wrap_pyfunction!(get_image_size, m)?)?;
    m.add_function(wrap_pyfunction!(get_image_size_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(set_num_threads, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    
    Ok(())
}
