import sys

# Try to import matlabengine. It might not be available depending on the environment.
try:
    import matlab.engine
    MATLAB_AVAILABLE = True
except ImportError:
    MATLAB_AVAILABLE = False
    print("WARNING: matlabengine is not installed or configured. MATLAB features will be mocked.")

_engine = None

def get_matlab_engine():
    global _engine
    if not MATLAB_AVAILABLE:
        return None
    if _engine is None:
        print("Starting MATLAB engine...")
        _engine = matlab.engine.start_matlab()
    return _engine

def run_fft(signal_data: list[float]) -> dict:
    """
    Calls MATLAB to perform Fast Fourier Transform (FFT) on a signal.
    """
    engine = get_matlab_engine()
    
    if engine is None:
        # Mocking the FFT result if MATLAB is not available
        return {
            "dominant_frequency": 50.0,
            "message": "MOCK: MATLAB engine not available. Mocked FFT result."
        }
        
    try:
        # Convert python list to MATLAB array
        matlab_array = matlab.double(signal_data)
        
        # In a real scenario, you'd call a custom .m script or built-in functions
        # e.g., result = engine.my_custom_fft_script(matlab_array)
        # Here we mock the interaction assuming a simple max value check as a proxy
        max_val = engine.max(matlab_array)
        
        return {
            "max_value": float(max_val),
            "message": "Successfully called MATLAB engine."
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to execute MATLAB function."
        }
