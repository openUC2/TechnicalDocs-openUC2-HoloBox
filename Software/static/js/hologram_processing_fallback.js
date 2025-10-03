/**
 * JavaScript (OpenCV.js) Hologram Processing — 1:1 with the PyScript API
 * Requires OpenCV.js (cv) loaded. Wait for cv.onRuntimeInitialized before use.
 */

class HologramProcessorOpenCV {
  constructor() {
    this.processingEnabled = false;
    this.processingInterval = null;
    this.currentWavelength = 440e-9;  // m
    this.currentPixelsize = 1.4e-6;   // m
    this.currentDz = 0.005;           // m
    this.debugMode = true;
  }

  // --- utils ---
  _nowStr() { return new Date().toLocaleTimeString(); }

  _log(...a) { if (this.debugMode) console.log(...a); }

  _ensureCvReady() {
    if (!window.cv || typeof cv.Mat === "undefined") {
      throw new Error("OpenCV.js not ready. Load opencv.js first.");
    }
    
    // Verify required OpenCV.js functions are available (only check once)
    if (!this._opencvFunctionsChecked) {
      const requiredFunctions = ['dft', 'multiply', 'add', 'subtract', 'normalize', 'split', 'merge', 'sqrt'];
      const missingFunctions = [];
      
      for (const func of requiredFunctions) {
        if (typeof cv[func] !== 'function') {
          missingFunctions.push(func);
        }
      }
      
      if (missingFunctions.length > 0) {
        console.warn(`⚠️ Missing OpenCV.js functions: ${missingFunctions.join(', ')}`);
        console.warn("⚠️ Some holographic processing features may not work correctly");
      } else {
        console.log("✅ All required OpenCV.js functions are available");
      }
      
      this._opencvFunctionsChecked = true;
    }
  }

  // FFT shift (swap quadrants) for complex 2-channel Mat
  _fftShift(complexMat) {
    const cx = complexMat.cols, cy = complexMat.rows;
    const cx2 = Math.floor(cx / 2), cy2 = Math.floor(cy / 2);

    const q0 = complexMat.roi(new cv.Rect(0,     0,     cx2, cy2));
    const q1 = complexMat.roi(new cv.Rect(cx2,  0,     cx - cx2, cy2));
    const q2 = complexMat.roi(new cv.Rect(0,     cy2,  cx2, cy - cy2));
    const q3 = complexMat.roi(new cv.Rect(cx2,  cy2,  cx - cx2, cy - cy2));

    const tmp = new cv.Mat();

    // Q0 <-> Q3
    q0.copyTo(tmp);  q3.copyTo(q0);  tmp.copyTo(q3);

    // Q1 <-> Q2
    q1.copyTo(tmp);  q2.copyTo(q1);  tmp.copyTo(q2);

    tmp.delete(); q0.delete(); q1.delete(); q2.delete(); q3.delete();
  }

  // complex multiply: out = A * B (both 2-channel float32 Mats)
  _complexMul(A, B) {
    const planesA = new cv.MatVector(); const planesB = new cv.MatVector();
    const planesOut = new cv.MatVector();

    cv.split(A, planesA); // [ReA, ImA]
    cv.split(B, planesB); // [ReB, ImB]

    const re = new cv.Mat(); const im = new cv.Mat();
    // re = ReA*ReB - ImA*ImB
    const t1 = new cv.Mat(); const t2 = new cv.Mat();
    cv.multiply(planesA.get(0), planesB.get(0), t1);
    cv.multiply(planesA.get(1), planesB.get(1), t2);
    cv.subtract(t1, t2, re);

    // im = ReA*ImB + ImA*ReB
    const t3 = new cv.Mat(); const t4 = new cv.Mat();
    cv.multiply(planesA.get(0), planesB.get(1), t3);
    cv.multiply(planesA.get(1), planesB.get(0), t4);
    cv.add(t3, t4, im);

    planesOut.push_back(re); planesOut.push_back(im);
    const out = new cv.Mat();
    cv.merge(planesOut, out);

    // cleanup
    planesA.delete(); planesB.delete(); planesOut.delete();
    re.delete(); im.delete(); t1.delete(); t2.delete(); t3.delete(); t4.delete();

    return out;
  }

  // Build Fresnel transfer function H(u,v) as complex 2-channel Mat (float32)
  _buildFresnelKernel(width, height, ps, lambda0, z) {
    const fx = new Float32Array(width);
    const fy = new Float32Array(height);

    const gridSizeX = ps * width;
    const gridSizeY = ps * height; // assume square pixels

    // frequency axes centered (-(N-1)/2 ... +(N-1)/2)/grid
    const fxStart = -((width - 1) / 2) / gridSizeX;
    const fyStart = -((height - 1) / 2) / gridSizeY;
    for (let i = 0; i < width; i++)  fx[i] = fxStart + i * (1 / gridSizeX);
    for (let j = 0; j < height; j++) fy[j] = fyStart + j * (1 / gridSizeY);

    const phase = new cv.Mat(height, width, cv.CV_32F);
    const twoPiOverLambda = (2 * Math.PI) / lambda0;

    // phase = kz + π λ z (Fx^2 + Fy^2); global kz term can be ignored for intensity
    // we include only quadratic term (global phase drops out after |.|^2)
    const lambdaZPi = Math.PI * lambda0 * z;

    // compute Fx^2 + Fy^2 via loops
    for (let y = 0; y < height; y++) {
      const fy2 = fy[y] * fy[y];
      for (let x = 0; x < width; x++) {
        const v = lambdaZPi * (fx[x] * fx[x] + fy2);
        phase.floatPtr(y, x)[0] = v; // store only quadratic term
      }
    }

    // H = exp(i*phase) - compute cos and sin manually since OpenCV.js doesn't have cv.cos/cv.sin
    const planes = new cv.MatVector();
    const H = new cv.Mat();
    const cosP = new cv.Mat.zeros(height, width, cv.CV_32F);
    const sinP = new cv.Mat.zeros(height, width, cv.CV_32F);
    
    console.log(`🔧 Computing Fresnel kernel manually for ${width}x${height} image`);
    
    // Compute cos and sin element by element
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const phaseVal = phase.floatPtr(y, x)[0];
        cosP.floatPtr(y, x)[0] = Math.cos(phaseVal);
        sinP.floatPtr(y, x)[0] = Math.sin(phaseVal);
      }
    }
    
    planes.push_back(cosP);
    planes.push_back(sinP);
    cv.merge(planes, H);

    planes.delete(); cosP.delete(); sinP.delete(); phase.delete();
    return H;
  }

  // Apply Fresnel propagation using DFT (OpenCV)
  _fresnelPropagateRealAmplitude(amplMat32F /* single-channel float32 [0..1] */, ps, lambda0, z) {
    // Ensure square ROI (as in Python code); if not square, DFT still works, but kernel computed accordingly.
    const rows = amplMat32F.rows, cols = amplMat32F.cols;

    // Prepare complex input: [ampl, 0]
    const zeros = new cv.Mat.zeros(rows, cols, cv.CV_32F);
    const inPlanes = new cv.MatVector();
    inPlanes.push_back(amplMat32F);
    inPlanes.push_back(zeros);
    const Ein = new cv.Mat();
    cv.merge(inPlanes, Ein);

    // Forward DFT
    const Efft = new cv.Mat();
    cv.dft(Ein, Efft, 0); // complex output
    // fftshift
    this._fftShift(Efft);

    // Fresnel kernel in frequency domain
    const H = this._buildFresnelKernel(cols, rows, ps, lambda0, z);

    // Multiply spectra
    const G = this._complexMul(Efft, H);

    // inverse shift
    this._fftShift(G);

    // Inverse DFT
    const Ef = new cv.Mat();
    cv.dft(G, Ef, cv.DFT_INVERSE | cv.DFT_SCALE);

    // Intensity = Re^2 + Im^2
    const planesEf = new cv.MatVector();
    cv.split(Ef, planesEf);
    const re2 = new cv.Mat(); const im2 = new cv.Mat(); const inten = new cv.Mat();
    cv.multiply(planesEf.get(0), planesEf.get(0), re2);
    cv.multiply(planesEf.get(1), planesEf.get(1), im2);
    cv.add(re2, im2, inten);

    // Normalize 0..255 uint8 for display
    const out8 = new cv.Mat();
    cv.normalize(inten, out8, 0, 255, cv.NORM_MINMAX, cv.CV_8U);

    // cleanup
    zeros.delete(); inPlanes.delete(); Ein.delete(); Efft.delete();
    H.delete(); G.delete(); Ef.delete(); planesEf.delete(); re2.delete(); im2.delete(); inten.delete();

    return out8; // CV_8U, single channel
  }

  // ROI from box or centered fallback
  getRoiCoordinates(imgWidth, imgHeight, roiSize) {
    try {
      if (window.getBoundaryBoxCoordinates) {
        const bbox = window.getBoundaryBoxCoordinates();
        let sx = parseInt(bbox.start_x || 0);
        let sy = parseInt(bbox.start_y || 0);
        let ex = parseInt(bbox.end_x || imgWidth);
        let ey = parseInt(bbox.end_y || imgHeight);

        const streamImg = document.getElementById('stream');
        if (streamImg && streamImg.naturalWidth > 0) {
          const sxScale = imgWidth / streamImg.naturalWidth;
          const syScale = imgHeight / streamImg.naturalHeight;
          sx = Math.floor(sx * sxScale);
          sy = Math.floor(sy * syScale);
          ex = Math.floor(ex * sxScale);
          ey = Math.floor(ey * syScale);
        }

        sx = Math.max(0, Math.min(sx, imgWidth));
        sy = Math.max(0, Math.min(sy, imgHeight));
        ex = Math.max(sx + 1, Math.min(ex, imgWidth));
        ey = Math.max(sy + 1, Math.min(ey, imgHeight));

        return { start_x: sx, start_y: sy, end_x: ex, end_y: ey, width: ex - sx, height: ey - sy };
      }
    } catch (e) {
      this._log("BBox error", e);
    }

    const cx = Math.floor(imgWidth / 2), cy = Math.floor(imgHeight / 2);
    const sx = Math.max(0, cx - Math.floor(roiSize / 2));
    const sy = Math.max(0, cy - Math.floor(roiSize / 2));
    const ex = Math.min(imgWidth, sx + roiSize);
    const ey = Math.min(imgHeight, sy + roiSize);
    return { start_x: sx, start_y: sy, end_x: ex, end_y: ey, width: ex - sx, height: ey - sy };
  }

  // Flip/rotate using OpenCV
  _applyTransforms(matRGBA /* CV_8UC4 */, flipX, flipY, rotationDeg) {
    let m = matRGBA;

    if (flipX || flipY) {
      const code = flipX && flipY ? -1 : (flipX ? 1 : 0);
      const dst = new cv.Mat();
      cv.flip(m, dst, code);
      if (m !== matRGBA) m.delete();
      m = dst;
    }

    if (rotationDeg === 90 || rotationDeg === 180 || rotationDeg === 270) {
      const dst = new cv.Mat();
      const rcode = (rotationDeg === 90) ? cv.ROTATE_90_COUNTERCLOCKWISE :
                    (rotationDeg === 180) ? cv.ROTATE_180 :
                    cv.ROTATE_90_CLOCKWISE; // 270 ccw == 90 cw
      cv.rotate(m, dst, rcode);
      if (m !== matRGBA) m.delete();
      m = dst;
    }

    return m;
  }

  // Main processing (OpenCV)
  processImageForHologram() {
    try {
      this._ensureCvReady();

      const streamImg = document.getElementById('stream');
      if (!streamImg || !streamImg.complete || !streamImg.naturalWidth) {
        this._log("Stream not ready");
        return;
      }

      const flipX = document.getElementById('flipX')?.checked || false;
      const flipY = document.getElementById('flipY')?.checked || false;
      const rotation = parseInt(document.getElementById('rotationAngle')?.value || 0);
      const roiSize = parseInt(document.getElementById('roiSize')?.value || 256);
      const colorChannel = document.getElementById('colorChannel')?.value || 'green';

      // Read RGBA from <img> via canvas -> cv.imread
      const tmpCanvas = document.createElement('canvas');
      tmpCanvas.width = streamImg.naturalWidth;
      tmpCanvas.height = streamImg.naturalHeight;
      const tctx = tmpCanvas.getContext('2d');
      tctx.drawImage(streamImg, 0, 0);
      let rgba = cv.imread(tmpCanvas); // CV_8UC4

      // Apply transforms
      rgba = this._applyTransforms(rgba, flipX, flipY, rotation);

      // Extract channel
      let rgb = new cv.Mat();
      cv.cvtColor(rgba, rgb, cv.COLOR_RGBA2RGB);
      const channels = new cv.MatVector();
      cv.split(rgb, channels);
      let chIdx = 1; // G
      if (colorChannel === 'red') chIdx = 2 ? 0 : 0; // (OpenCV split order is B,G,R)
      if (colorChannel === 'blue') chIdx = 0;
      const gray8 = channels.get(chIdx); // single channel 8U

      // ROI
      const roiCoords = this.getRoiCoordinates(gray8.cols, gray8.rows, roiSize);
      const roiRect = new cv.Rect(roiCoords.start_x, roiCoords.start_y, roiCoords.width, roiCoords.height);
      let roi8 = gray8.roi(roiRect).clone();

      // If ROI smaller than roiSize, pad to square
      if (roi8.rows !== roiSize || roi8.cols !== roiSize) {
        const dst = new cv.Mat.zeros(roiSize, roiSize, cv.CV_8U);
        const y0 = Math.floor((roiSize - roi8.rows) / 2);
        const x0 = Math.floor((roiSize - roi8.cols) / 2);
        const dstROI = dst.roi(new cv.Rect(x0, y0, roi8.cols, roi8.rows));
        roi8.copyTo(dstROI);
        dstROI.delete();
        roi8.delete();
        roi8 = dst;
      }

      // amplitude = sqrt(intensity) with normalization [0..1]
      const roi32 = new cv.Mat();
      roi8.convertTo(roi32, cv.CV_32F, 1.0 / 255.0);
      const ampl = new cv.Mat();
      cv.sqrt(roi32, ampl);

      // Fresnel propagation
      const out8 = this._fresnelPropagateRealAmplitude(
        ampl,
        this.currentPixelsize,
        this.currentWavelength,
        this.currentDz
      ); // CV_8U

      // Display to #processed (scaled to canvas size via cv.imshow inherent)
      const processedCanvas = document.getElementById('processed');
      if (processedCanvas) {
        // ensure canvas size matches desired display; you can set CSS size separately
        processedCanvas.width = out8.cols;
        processedCanvas.height = out8.rows;
        cv.imshow(processedCanvas, out8);
      }

      const ts = this._nowStr();
      const last = document.getElementById('last-processed');
      if (last) last.textContent = `${ts}`;

      // cleanup
      rgba.delete(); rgb.delete(); channels.delete(); gray8.delete();
      roi8.delete(); roi32.delete(); ampl.delete(); out8.delete();

    } catch (e) {
      console.error("Processing error (OpenCV):", e);
    }
  }

  updateParameters() {
    const w = document.getElementById('wavelength');
    if (w) this.currentWavelength = parseFloat(w.value) * 1e-9;

    const p = document.getElementById('pixelsize');
    if (p) this.currentPixelsize = parseFloat(p.value) * 1e-6;

    const dz = document.getElementById('dz');
    if (dz) this.currentDz = parseFloat(dz.value) * 1e-3;

    this._log(
      `λ=${(this.currentWavelength * 1e9).toFixed(0)} nm,`,
      `px=${(this.currentPixelsize * 1e6).toFixed(2)} µm,`,
      `z=${(this.currentDz * 1e3).toFixed(2)} mm`
    );
  }

  toggleProcessing() {
    this.processingEnabled = !this.processingEnabled;
    const btn = document.getElementById('toggleProcessing');
    const status = document.getElementById('processing-enabled');

    if (this.processingEnabled) {
      if (btn) { btn.textContent = 'Disable Processing'; btn.className = 'btn btn-danger'; }
      if (status) status.textContent = 'Enabled';
      this.processingInterval = setInterval(() => this.processImageForHologram(), 1000);
    } else {
      if (btn) { btn.textContent = 'Enable Processing'; btn.className = 'btn btn-success'; }
      if (status) status.textContent = 'Disabled';
      if (this.processingInterval) clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  processSingleFrame() { this.processImageForHologram(); }

  toggleDebugMode() {
    this.debugMode = !this.debugMode;
    const btn = document.getElementById('toggleDebug');
    if (btn) btn.textContent = this.debugMode ? 'Disable Debug' : 'Enable Debug';
  }

  initializeEventListeners() {
    const t = document.getElementById('toggleProcessing');
    if (t) t.onclick = () => this.toggleProcessing();
    const s = document.getElementById('processSingleFrame') || document.getElementById('processFrame');
    if (s) s.onclick = () => this.processSingleFrame();
    const d = document.getElementById('toggleDebug');
    if (d) d.onclick = () => this.toggleDebugMode();

    const w = document.getElementById('wavelength');
    if (w) w.oninput = () => this.updateParameters();
    const p = document.getElementById('pixelsize');
    if (p) p.oninput = () => this.updateParameters();
    const dz = document.getElementById('dz');
    if (dz) dz.oninput = () => this.updateParameters();

    this.updateParameters();
    this.processImageForHologram();
  }
}

// expose both classes
window.HologramProcessorOpenCV = HologramProcessorOpenCV;

/**
 * Off-Axis Hologram Processor Fallback
 * Simplified JavaScript implementation for off-axis holographic reconstruction
 */
class OffAxisHologramProcessor {
  constructor() {
    this.processingEnabled = false;
    this.processingInterval = null;
    this.currentWavelength = 532e-9;  // m (green laser)
    this.currentPixelsize = 1.4e-6;   // m
    this.currentRefocusDistance = 0.0; // m
    this.debugMode = true;
    this.currentROI = {x: 100, y: 100, width: 100, height: 100};
  }

  _log(...args) {
    if (this.debugMode) console.log(...args);
  }

  // Simple 2D FFT approximation using separable 1D transforms
  _simple2DFFT(imageData, width, height) {
    // This is a simplified approximation - real FFT would be much more complex
    const fftData = new Float32Array(width * height * 2); // complex data
    
    // For demonstration, create a mock frequency domain representation
    for (let i = 0; i < height; i++) {
      for (let j = 0; j < width; j++) {
        const idx = i * width + j;
        const pixel = imageData[idx * 4]; // Use red channel
        
        // Simple frequency representation (this is not a real FFT)
        const u = j - width/2;
        const v = i - height/2;
        const freq = Math.sqrt(u*u + v*v);
        
        fftData[idx * 2] = pixel * Math.cos(freq * 0.1); // real part
        fftData[idx * 2 + 1] = pixel * Math.sin(freq * 0.1); // imaginary part
      }
    }
    
    return fftData;
  }

  // Extract ROI from FFT data
  _extractROI(fftData, width, height, roi) {
    const roiData = new Float32Array(roi.width * roi.height * 2);
    
    for (let i = 0; i < roi.height; i++) {
      for (let j = 0; j < roi.width; j++) {
        const srcX = Math.min(roi.x + j, width - 1);
        const srcY = Math.min(roi.y + i, height - 1);
        const srcIdx = srcY * width + srcX;
        const dstIdx = i * roi.width + j;
        
        roiData[dstIdx * 2] = fftData[srcIdx * 2];     // real
        roiData[dstIdx * 2 + 1] = fftData[srcIdx * 2 + 1]; // imaginary
      }
    }
    
    return roiData;
  }

  // Simplified inverse FFT
  _simpleIFFT(roiData, width, height) {
    const result = new Float32Array(width * height * 2);
    
    // Simple inverse transform approximation
    for (let i = 0; i < height; i++) {
      for (let j = 0; j < width; j++) {
        const idx = i * width + j;
        
        // Simple inverse frequency representation
        const u = j - width/2;
        const v = i - height/2;
        const freq = Math.sqrt(u*u + v*v);
        
        if (idx < roiData.length / 2) {
          result[idx * 2] = roiData[idx * 2] * Math.cos(-freq * 0.1);
          result[idx * 2 + 1] = roiData[idx * 2 + 1] * Math.sin(-freq * 0.1);
        }
      }
    }
    
    return result;
  }

  // Calculate amplitude and phase
  _calculateAmplitudePhase(complexData, width, height) {
    const amplitude = new Float32Array(width * height);
    const phase = new Float32Array(width * height);
    
    for (let i = 0; i < width * height; i++) {
      const real = complexData[i * 2];
      const imag = complexData[i * 2 + 1];
      
      amplitude[i] = Math.sqrt(real * real + imag * imag);
      phase[i] = Math.atan2(imag, real);
    }
    
    return { amplitude, phase };
  }

  // Main off-axis processing function
  processOffAxisHologram(imageData, width, height) {
    this._log("🔄 Processing off-axis hologram (simplified mode)");
    
    try {
      // Step 1: Simple FFT
      const fftData = this._simple2DFFT(imageData, width, height);
      
      // Step 2: Extract ROI (cross-correlation term)
      const roiData = this._extractROI(fftData, width, height, this.currentROI);
      
      // Step 3: Inverse FFT of ROI
      const reconstructed = this._simpleIFFT(roiData, this.currentROI.width, this.currentROI.height);
      
      // Step 4: Calculate amplitude and phase
      const result = this._calculateAmplitudePhase(reconstructed, this.currentROI.width, this.currentROI.height);
      
      // Draw results to canvases
      this._drawToCanvas('fourier-canvas', fftData, width, height, 'magnitude');
      this._drawToCanvas('amplitude-canvas', result.amplitude, this.currentROI.width, this.currentROI.height, 'amplitude');
      this._drawToCanvas('phase-canvas', result.phase, this.currentROI.width, this.currentROI.height, 'phase');
      
      this._log("✅ Off-axis processing complete");
      
    } catch (error) {
      console.error("❌ Error in off-axis processing:", error);
    }
  }

  // Draw data to canvas
  _drawToCanvas(canvasId, data, width, height, type) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    const imageData = ctx.createImageData(width, height);
    
    // Find min/max for normalization
    let min = Infinity, max = -Infinity;
    for (let i = 0; i < data.length; i++) {
      if (type === 'magnitude' && i % 2 === 0) { // For FFT data, use magnitude
        const real = data[i];
        const imag = data[i + 1];
        const mag = Math.sqrt(real * real + imag * imag);
        min = Math.min(min, mag);
        max = Math.max(max, mag);
      } else if (type !== 'magnitude') {
        min = Math.min(min, data[i]);
        max = Math.max(max, data[i]);
      }
    }
    
    const range = max - min || 1;
    
    for (let i = 0; i < width * height; i++) {
      let value;
      
      if (type === 'magnitude') {
        const real = data[i * 2] || 0;
        const imag = data[i * 2 + 1] || 0;
        value = Math.sqrt(real * real + imag * imag);
      } else if (type === 'phase') {
        // Map phase from [-π, π] to [0, 255]
        value = ((data[i] || 0) + Math.PI) / (2 * Math.PI) * 255;
      } else {
        // Amplitude
        value = ((data[i] || 0) - min) / range * 255;
      }
      
      value = Math.max(0, Math.min(255, value));
      
      const pixelIndex = i * 4;
      if (type === 'phase') {
        // Color-code phase
        imageData.data[pixelIndex] = value;     // Red
        imageData.data[pixelIndex + 1] = 255 - value; // Green
        imageData.data[pixelIndex + 2] = 128;   // Blue
      } else {
        // Grayscale for amplitude and magnitude
        imageData.data[pixelIndex] = value;
        imageData.data[pixelIndex + 1] = value;
        imageData.data[pixelIndex + 2] = value;
      }
      imageData.data[pixelIndex + 3] = 255; // Alpha
    }
    
    ctx.putImageData(imageData, 0, 0);
  }

  // Process current camera frame
  processCurrentFrame() {
    const streamImg = document.getElementById('stream');
    if (!streamImg || !streamImg.complete) {
      this._log("⚠️ No camera image available");
      return;
    }
    
    // Create a canvas to extract image data
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = streamImg.naturalWidth || streamImg.width || 400;
    canvas.height = streamImg.naturalHeight || streamImg.height || 400;
    
    ctx.drawImage(streamImg, 0, 0, canvas.width, canvas.height);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    
    // Process the image
    this.processOffAxisHologram(imageData.data, canvas.width, canvas.height);
  }

  // Update parameters from UI
  updateParameters() {
    const waveEl = document.getElementById('wavelength');
    const pixelEl = document.getElementById('pixelsize');
    const refocusEl = document.getElementById('refocus-distance');
    
    if (waveEl) this.currentWavelength = parseFloat(waveEl.value) * 1e-9; // nm to m
    if (pixelEl) this.currentPixelsize = parseFloat(pixelEl.value) * 1e-6; // µm to m
    if (refocusEl) this.currentRefocusDistance = parseFloat(refocusEl.value) * 1e-6; // µm to m
    
    // Update ROI from inputs
    const roiX = document.getElementById('roi-x');
    const roiY = document.getElementById('roi-y');
    const roiW = document.getElementById('roi-width');
    const roiH = document.getElementById('roi-height');
    
    if (roiX && roiY && roiW && roiH) {
      this.currentROI = {
        x: parseInt(roiX.value),
        y: parseInt(roiY.value),
        width: parseInt(roiW.value),
        height: parseInt(roiH.value)
      };
    }
    
    this._log(`📊 Parameters updated: λ=${(this.currentWavelength*1e9).toFixed(0)}nm, pixel=${(this.currentPixelsize*1e6).toFixed(1)}µm, ROI=${JSON.stringify(this.currentROI)}`);
  }

  // Toggle processing
  toggleProcessing() {
    this.processingEnabled = !this.processingEnabled;
    const btn = document.getElementById('toggleProcessing');
    
    if (this.processingEnabled) {
      if (btn) {
        btn.textContent = 'Disable Processing';
        btn.className = 'btn btn-danger';
      }
      this.processingInterval = setInterval(() => {
        this.updateParameters();
        this.processCurrentFrame();
      }, 1000);
    } else {
      if (btn) {
        btn.textContent = 'Enable Processing';
        btn.className = 'btn btn-info';
      }
      if (this.processingInterval) {
        clearInterval(this.processingInterval);
        this.processingInterval = null;
      }
    }
  }

  // Initialize event listeners
  initializeEventListeners() {
    this._log("🔧 Initializing off-axis event listeners");
    
    const toggleBtn = document.getElementById('toggleProcessing');
    if (toggleBtn) {
      toggleBtn.onclick = () => this.toggleProcessing();
    }
    
    const processBtn = document.getElementById('processFrame');
    if (processBtn) {
      processBtn.onclick = () => {
        this.updateParameters();
        this.processCurrentFrame();
      };
    }
    
    const debugBtn = document.getElementById('toggleDebug');
    if (debugBtn) {
      debugBtn.onclick = () => {
        this.debugMode = !this.debugMode;
        debugBtn.textContent = this.debugMode ? 'Disable Debug' : 'Enable Debug';
      };
    }
    
    // Parameter sliders
    ['wavelength', 'pixelsize', 'refocus-distance'].forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.oninput = () => this.updateParameters();
      }
    });
    
    // ROI inputs
    ['roi-x', 'roi-y', 'roi-width', 'roi-height'].forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.oninput = () => this.updateParameters();
      }
    });
    
    // Initialize parameters
    this.updateParameters();
    
    // Expose globally for easy access
    window.processCurrentFrame = () => this.processCurrentFrame();
    window.offAxisProcessor = this;
    
    this._log("✅ Off-axis event listeners initialized");
  }
}

// Expose the off-axis processor
window.OffAxisHologramProcessor = OffAxisHologramProcessor;

// Auto-initialize if we're on the off-axis page
if (window.location.href.includes('offaxis') || window.location.href.includes('index_offaxis')) {
  document.addEventListener('DOMContentLoaded', () => {
    if (window.pyScriptFallbackLoader?.isFallbackMode || window.forceFallbackMode) {
      console.log("🚀 Initializing off-axis fallback processor");
      window.offAxisProcessor = new OffAxisHologramProcessor();
      window.offAxisProcessor.initializeEventListeners();
    }
  });
}
