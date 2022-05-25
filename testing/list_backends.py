import cv2

backends = cv2.videoio_registry.getBackends()
for api in backends:
    print(cv2.videoio_registry.getBackendName(api))