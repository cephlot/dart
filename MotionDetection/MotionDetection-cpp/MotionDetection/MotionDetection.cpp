#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <iostream>

using namespace cv;

int main() {
	VideoCapture cap(1);

	if(!cap.isOpened()) {
		std::cout << std::endl << "cannot open camera" << std::endl << std::endl;
		return 1;
	}

	cap.set(CAP_PROP_FRAME_WIDTH, 1280);
	cap.set(CAP_PROP_FRAME_HEIGHT, 720);

	const double scale = 0.7;
	Mat last_frame;
	cap >> last_frame;
	resize(last_frame, last_frame, Size(), scale, scale);
	cvtColor(last_frame, last_frame, COLOR_BGR2GRAY);
	GaussianBlur(last_frame, last_frame, Size(5, 5), 0.0);
	while (true) {
		Mat frame;
		cap >> frame;
		resize(frame, frame, Size(), scale, scale);

		Mat frame_gray;
		cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
		
		GaussianBlur(frame_gray, frame_gray, Size(5,5), 0.0);
		
		Mat frame_diff;
		absdiff(frame_gray, last_frame, frame_diff);

		frame_gray.copyTo(last_frame);

		threshold(frame_diff, frame_diff, 40, 255, THRESH_BINARY);
		imshow("Threshold", frame_diff);

		std::vector<std::vector<Point> > contours;
		std::vector<Vec4i> hierarchy;
		findContours(frame_diff, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

		for (std::vector<Point> contour : contours) {
			if (contourArea(contour) < 50.0) {
				continue;
			}
			Rect rect = boundingRect(contour);
			rectangle(frame, rect, Scalar(0,255,0), 2);
		}

		imshow("Input", frame);

		if (countNonZero(frame_diff) > 0) {
			std::cout << "Detected motion!" << std::endl;
		}

		int key = waitKey(1);
		if (key != -1) {
			break;
		}
	}

	cap.release();
	destroyAllWindows();
	return 0;
}