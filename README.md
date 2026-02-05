# AbsensiPro: AI-Powered Face Recognition Attendance System

**Modern Dark Glassmorphism Interface for Real-Time Biometric Verification.**

**Semester 1 Project - Programming Algorithm 1C**<br>
**Contributors: Class 1KB04 - Computer System - Gunadarma University**

---

## Abstract

**AbsensiPro** is a high-performance, real-time attendance management solution that integrates advanced computer vision algorithms with cloud technologies. Designed specifically for the **1KB04 Computer System class at Gunadarma University**, this system offers optimized detection accuracy and centralized database storage through MongoDB Atlas. It bridges the gap between traditional manual attendance and automated biometric security.

---

## Tech Stack

| Category          | Technology          | Logo/Badge                                                                                                                                                                                                                          |
| :---------------- | :------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Language**      | Python 3.11         | ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)                                                                                                                              |
| **Web Framework** | Flask               | ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)                                                                                                                              |
| **Frontend**      | Tailwind CSS / Vite | ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) |
| **Database**      | MongoDB Atlas       | ![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)                                                                                                                     |
| **Reporting**     | Google Sheets API   | ![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)                                                                                                        |
| **AI Engine**     | Dlib / OpenCV       | ![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)                                                                                                                         |

---

## Key Features

- **Real-time Recognition**: High-speed face detection and identification using optimized HOG algorithms.
- **Premium UI/UX**: State-of-the-art _Dark Glassmorphism_ design with smooth micro-animations and a dynamic scanning line.
- **Responsive Design**: Fully optimized for Desktop and Mobile with a floating glass navigation bar.
- **Admin Dashboard**: Secure terminal for biometric registration, user management, and real-time log monitoring.
- **Hybrid Logging**: Simultaneous data synchronization with MongoDB Atlas for security and Google Sheets for administrative reporting.
- **Voice Feedback**: Integrated Smart Voice system for successful attendance confirmation.

---

## Algorithm Analysis (Theoretical Framework)

The system implements a multi-stage biometric processing pipeline based on modern computer vision principles. The architecture utilizes a combination of Histogram of Oriented Gradients (HOG) and Deep Metric Learning via ResNet-34.

### 1. Image Pre-processing & Normalization

Incoming frames from the Base64 stream undergo linear pixel transformation to enhance contrast and brightness, ensuring robust detection under varying lighting conditions.
$$g(x,y) = \alpha \cdot I(x,y) + \beta$$ <br>
_(Where α=1.1 and β=10 optimize the dynamic range)._

### 2. Face Detection: HOG & Linear SVM

The system identifies facial bounding boxes using the HOG algorithm classified by a Linear Support Vector Machine.

<img src="https://media.geeksforgeeks.org/wp-content/uploads/20250605131337992934/Output-Image.jpg" width="700" />

**A. HOG Feature Extraction**: The algorithm calculates pixel intensity gradients to capture the structural contour of the face.

- **Gradient Magnitude**: $M(x,y) = \sqrt{G_x(x,y)^2 + G_y(x,y)^2}$
- **Gradient Orientation**: $\theta(x,y) = \arctan\left(\frac{G_y(x,y)}{G_x(x,y)}\right)$

<img src="https://user-images.githubusercontent.com/69381013/210751911-ecfa8517-eb60-4d47-b69a-164137d24ed1.png" width="700" />

**B. Classification (Linear SVM)**: Features are processed by a hyperplane designed for binary classification (Face vs. Non-Face).
$$f(x) = \text{sign}(w^T x + b)$$

### 3. Feature Extraction: 128-D Deep Metric Learning

Cropped facial regions are passed through a deep convolutional neural network (ResNet-34) to generate a unique 128-dimensional embedding vector $v$.
$$v = f_{ResNet}(x)$$

### 4. Identity Mapping: Euclidean Distance Matching

Identities are determined by calculating the $L_2$ distance between the input vector ($S$) and the registered database vectors ($V$).
$$dist(S,V) = \sqrt{\sum_{i=1}^{128}(S_i - V_i)^2}$$
Identities are confirmed when $dist(S, V_k) < T$, where $T = 0.5$ is the optimized matching threshold.

---

## Installation Guide

To ensure a smooth setup across all platforms (Windows, Linux, macOS), follow the specific requirements below. The most common error during installation is lack of `cmake` for compiling `dlib`.

### 1. Environment Requirements

- **Python**: 3.11 or higher.
- **Node.js**: 20 or higher.
- **C++ Compiler**:
  - **Windows**: [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Select "Desktop development with C++"). or install with winget on powershell (as Administrator) `winget install Kitware.CMake`
  - **macOS**: `xcode-select --install` and `brew install cmake`.
  - **Linux**: `sudo apt install build-essential cmake libgtk-3-dev libboost-all-dev`.

### 2. Local Setup

```bash
# Clone the repository
git clone https://github.com/Dickybulin26/face_attendance_1kb04.git
cd face_attendance_1kb04
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Create `credentials.json` file for Google Sheets API and place it in the root directory of the project.

```bash
touch credentials.json
```

Fill in the following variables in `.env`:

- `MONGO_URI`: Your MongoDB Atlas connection string.
- `GOOGLE_SHEETS_CREDENTIALS`: Path to your `credentials.json`.
- `GOOGLE_SHEETS_NAME`: Your spreadsheet title.

### 4. Launching the System

```bash
# Add Permission (linux only)
chmod +x run_app.sh

# Run app
./run_app.sh
```

Access at `http://localhost:5000`

---

Access at `http://localhost:5000`

---

## Production Deployment (Recommended)

The system includes a production-ready `deploy.sh` script to manage the Docker lifecycle.

### 1. Configure Environment

Prepare your `.env` and `credentials.json` as described in the Installation Guide.

### 2. Manage with Deploy Script

```bash
chmod +x deploy.sh

# Build and start the system
./deploy.sh build
./deploy.sh start

# Check status
./deploy.sh status
```

Access at `http://localhost:1324`

### 3. Utility Commands

- `./deploy.sh stop` - Stop the system
- `./deploy.sh logs` - View real-time logs
- `./deploy.sh restart` - Restart the container

---

---

## Docker Pull From DockerHub Repository

It will pull the image from DockerHub and run it.
DockerHub repository: [dickyasqaelani/absensipro](https://hub.docker.com/r/dickyasqaelani/absensipro)

```bash
# Run the container
docker run -d -p 1324:1324 --name absensipro dickyasqaelani/absensipro:v1
```

---

## Operational Guide

1. **Administration**: Log in as admin to access the **Registration** menu.
2. **Registration**: Input the user's name and capture a clear face photo. The system will extract the biometric data locally.
3. **Scanning**: On the main dashboard, align the face within the guidelines. The system automatically verifies identity.
4. **Log Management**: View real-time logs in the **History** section. Data is automatically synced to your connected Google Sheet.

---

## Technical Considerations

- **Lighting**: For optimal results, ensure the environment is well-lit and avoid backlighting.
- **Hardware**: A 720p webcam is recommended. Multi-platform support is optimized via Vite assets.
- **Process**: Facial data is processed into 128-D vectors; only anonymized mathematical embeddings are stored, not raw images.

---

## References

- Analysis of Face Recognition Algorithm: Dlib and OpenCV ([ResearchGate](https://www.researchgate.net/publication/343718108_Analysis_of_Face_Recognition_Algorithm_Dlib_and_OpenCV))
- Histogram of Oriented Gradients ([GeeksforGeeks](https://www.geeksforgeeks.org/computer-vision/histogram-of-oriented-gradients))
- C34 | HOG Feature Vector Calculation | Computer Vision | EvODN ([YouTube](https://youtu.be/28xk5i1_7Zc))
- C37 | Dalal & Triggs Object Detection | HOG + SVM | EvODN ([YouTube](https://youtu.be/sDByl84n5mY))
