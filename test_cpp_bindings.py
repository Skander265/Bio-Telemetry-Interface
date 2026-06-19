import sys
try:
    import bio_core_cpp
    print("SUCCESS: bio_core_cpp imported successfully!")
    
    filter = bio_core_cpp.MovingAverageFilter(5)
    print("Filter apply:", filter.apply(10.0))
    print("Filter apply:", filter.apply(20.0))
    
    analyst = bio_core_cpp.SignalAnalyst("test")
    print("Analyst update:", analyst.update(1.0))
    
    synth = bio_core_cpp.AudioSynthesizer()
    print("AudioSynthesizer created")
    
    port = bio_core_cpp.SerialReader.find_available_port()
    print("Available port:", port)
    
except ImportError as e:
    print(f"FAILED to import bio_core_cpp: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error during test: {e}")
    sys.exit(1)
