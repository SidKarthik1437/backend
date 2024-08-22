# NEXA Examination Platform - Backend

This repository hosts the backend for **NEXA**, an advanced, scalable examination platform focused on delivering efficient and secure assessments, particularly for Multiple Choice Questions (MCQs). The platform is designed to automate exam management while ensuring robust security, seamless user experience, and real-time evaluation.

## Key Features

- **User Management & Role-Based Access Control:**  
  Comprehensive user management with role-based access tailored for administrators, examiners, and students. The system supports hierarchical roles with granular permissions to manage diverse user activities.

- **Dynamic Exam Creation & Question Pooling:**  
  Flexible exam creation with dynamic question pools that allow automatic question assignment from predefined categories. This ensures fair and balanced exams with the option for randomization.

- **Security & Monitoring:**  
  Advanced security features such as tab/window change detection to prevent cheating, automatic version creation for question papers, and detailed activity logs for audit purposes.

- **Instant Evaluation & Result Processing:**  
  Real-time grading of exams with instant result generation, offering insights into student performance with detailed analytics.

- **Scalable Microservices Architecture:**  
  Built with a microservices approach, making it highly scalable and capable of handling large numbers of concurrent users. The system is designed for cloud-native deployment, leveraging Kubernetes for efficient orchestration.

- **Integration with Third-Party Services:**  
  Seamless integration with Clerk for authentication and Azure for CI/CD and deployment, ensuring smooth operations in both development and production environments.

## Tech Stack Overview

- **Backend Framework:** Python (Django), Django REST Framework
- **Database:** PostgreSQL / MongoDB (depending on the module)
- **Authentication & User Management:** Clerk
- **Containerization & Deployment:** Docker, Kubernetes
- **Cloud & CI/CD:** Azure DevOps, Kubernetes Service on Azure

## Project Purpose

The NEXA backend is engineered to minimize manual intervention in exam management, reduce operational inefficiencies, and promote sustainability by decreasing the dependency on physical resources like paper. Through automation and advanced analytics, NEXA aims to provide a seamless examination experience while maintaining integrity and enhancing user engagement.

**Note:** This repository is closed-source and contains proprietary code. Access is restricted.
