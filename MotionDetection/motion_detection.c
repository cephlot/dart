#include 
#include <opencv/cv.h>
int main(int argc,char **argv)
{
        cvNamedWindow(“rohit”,CV_WINDOW_AUTOSIZE);
        CvCapture* cap = cvCreateCameraCapture(0);
        IplImage *image1,*image2;
        while(1){
                image1  = cvQueryFrame(cap);
                if(!image1)
                        break;

                cvShowImage(“rohit”,image1);

//waiting 33 milliseconds for a key to be pressed

                char c = cvWaitKey(33);

//if the key pressed is esc
//ascii of esc is 27

                if(c==27)
                        break;
//if the key pressed is an up-arrow key
                else if(c ==’82’)
                {
                        image2 = image1;
                        cvNamedWindow(“rohit photo”,CV_WINDOW_AUTOSIZE);
                        cvShowImage(“rohit photo”,image2);
                        cvSaveImage(“my-photo.jpg”,image2);
                }
        }
        cvReleaseCapture(&cap);
        cvDestroyWindow(“rohit”);
        cvDestroyWindow(“rohit photo”);
}

