# 🧠 NeuralSync Live - AI-Powered Adaptive Learning Platform

[![Powered by Gemini 3](https://img.shields.io/badge/Powered%20by-Gemini%203-6366f1?style=for-the-badge)](https://ai.google.dev/)
[![Django](https://img.shields.io/badge/Django-5.2-092e20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python)](https://www.python.org/)

> **"Learning That Adapts to You"**  
> Transform any content into an interactive, personalized learning experience powered by Gemini 3's advanced AI.

---

## 🌟 Project Overview

**NeuralSync Live** is an innovative adaptive learning platform built for the **Gemini 3 Global Hackathon**. It leverages Google's cutting-edge Gemini 3 API to create four unique learning modes that transform passive content consumption into active, personalized educational experiences.

### 🎯 The Problem We Solve

Traditional learning tools deliver the same content to every student, regardless of their level, learning style, or comprehension speed. This one-size-fits-all approach leads to:
- Passive learning instead of active engagement
- Slow progress for advanced learners
- Frustration for struggling students
- Lack of real-time feedback and guidance

### 💡 Our Solution

NeuralSync Live uses **Gemini 3's multimodal capabilities** to:
1. **Analyze** any educational content (videos, images, documents)
2. **Adapt** to individual learning styles and comprehension levels
3. **Guide** users with Socratic questioning instead of direct answers
4. **Evolve** difficulty based on real-time performance

---

## ✨ Key Features & Gemini 3 Integration

### 🎥 **1. Learn While You Watch**
- **Upload educational videos** in any format (MP4, MOV, AVI, WEBM)
- **Gemini 3 analyzes** content in real-time using vision capabilities
- **Interactive questions** appear at key moments in the video
- **Adaptive difficulty** based on user responses
- **Smart timestamps** for easy navigation to important concepts

**Gemini 3 Features Used:**
- Multimodal video understanding
- Real-time content analysis
- Dynamic question generation
- Contextual reasoning

### 🧮 **2. Visual Problem Solver**
- **Snap photos** of math, physics, coding, or other problems
- **Socratic guidance** - Gemini 3 guides step-by-step without revealing answers
- **Hint system** that adapts to student progress
- **Practice problem generation** for similar concepts
- **Multi-subject support** (mathematics, physics, chemistry, programming, etc.)

**Gemini 3 Features Used:**
- Image recognition and OCR
- Step-by-step reasoning
- Socratic method implementation
- Adaptive hint generation

### 📄 **3. Document Intelligence**
- **Transform dense documents** (PDF, TXT, DOC) into interactive experiences
- **Concept mapping** - visualize relationships between ideas
- **Smart analogies** to simplify complex topics
- **Adaptive quizzes** with difficulty scaling
- **Key definitions** extracted automatically

**Gemini 3 Features Used:**
- Document understanding
- Concept extraction
- Relationship mapping
- Analogy generation
- Quiz creation

### 🎨 **4. Creative Workshop**
- **Upload designs, sketches,** or creative work
- **Expert feedback** on composition, technique, and aesthetics
- **Improvement suggestions** with priority ranking
- **Design principle** explanations
- **Variation generation** to explore alternatives

**Gemini 3 Features Used:**
- Visual design analysis
- Creative feedback generation
- Design principle understanding
- Variation ideation

---

## 🚀 Technical Architecture

### Backend (Django)
- **Django 5.2** - Modern Python web framework
- **RESTful API** for seamless frontend-backend communication
- **Session management** to track learning progress
- **File upload** with multiple format support
- **Database** (SQLite) for storing sessions, interactions, and analytics

### AI Integration
- **Google Generative AI SDK** (google-generativeai)
- **Gemini 2.0 Flash Exp** model for speed and multimodal capabilities
- **Streaming responses** for real-time interactions
- **Context preservation** across conversation turns
- **JSON parsing** for structured data extraction

### Frontend
- **Modern HTML5/CSS3/JavaScript** (no heavy frameworks for speed)
- **Responsive design** that works on all devices
- **Glassmorphism effects** and premium gradients
- **Smooth animations** using CSS and Intersection Observer
- **Real-time chat interface** with typing indicators
- **Drag-and-drop file upload**

### Design System
- **Custom CSS variables** for consistent theming
- **Dark theme first** with vibrant accent colors
- **Inter & Space Grotesk** fonts for modern typography
- **Micro-animations** for enhanced UX
- **Accessible** with semantic HTML

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Google Gemini 3 API Key ([Get one here](https://ai.google.dev/))

### Step 1: Clone the Repository
```bash
git clone https://github.com/heritiernkh/kachele_neural_sync.git
cd kachele_neural_sync
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_django_secret_key
```

### Step 5: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

### Step 8: Access the Application
Open your browser and navigate to:
- **Homepage:** http://localhost:8000/
- **Demo:** http://localhost:8000/demo/
- **Admin:** http://localhost:8000/admin/

---

## 🎮 How to Use

### Quick Start
1. **Visit the homepage** and click "Try Now"
2. **Select a learning mode** (Video, Problem, Document, or Creative)
3. **Upload your content** (drag-and-drop or browse)
4. **Wait for AI analysis** (typically 5-15 seconds)
5. **Engage interactively** with questions, hints, and feedback
6. **Track your progress** in the sidebar stats

### Pro Tips
- Use **high-quality images** for better OCR in Problem Solver mode
- Upload **educational videos** (lectures, tutorials) for best results
- Try the **hint system** before revealing answers
- Check **session stats** to track your accuracy and improvement

---

## 📊 Gemini 3 API Usage

### API Endpoints Created
| Endpoint | Method | Purpose | Gemini Feature |
|----------|--------|---------|----------------|
| `/api/session/create/` | POST | Create learning session | - |
| `/api/upload/` | POST | Upload & analyze content | Multimodal analysis |
| `/api/ask/` | POST | Ask questions | Conversational AI |
| `/api/answer/` | POST | Submit answers for evaluation | Reasoning & feedback |
| `/api/hint/` | POST | Request adaptive hints | Contextual guidance |
| `/api/practice/generate/` | POST | Generate practice problems | Content generation |

### Gemini Service Functions
```python
- analyze_video() - Video content analysis
- analyze_image_problem() - Visual problem solving
- analyze_document() - Document intelligence
- creative_workshop() - Design feedback
- start_interactive_session() - Chat initialization
- evaluate_answer() - Response evaluation
- generate_practice_problems() - Exercise creation
```

---

## 🏆 Why NeuralSync Live Stands Out

### 1. **Educational Impact**
- Promotes **active learning** over passive consumption
- Uses **Socratic method** - proven pedagogical technique
- **Adapts in real-time** to learner needs
- **Tracks progress** and identifies knowledge gaps

### 2. **Technical Excellence**
- **Full-stack implementation** with modern technologies
- **Clean architecture** with separation of concerns
- **Responsive design** that works everywhere
- **Performance optimized** for smooth interactions

### 3. **Innovation**
- **Four unique modes** showcasing Gemini 3 versatility
- **Multimodal integration** (text, image, video, documents)
- **Real-time adaptation** based on user interactions
- **Beautiful UI/UX** that inspires engagement

### 4. **Scalability**
- **Cloud-ready** architecture
- **API-first design** for future integrations
- **Extensible** to new learning modes
- **Market potential** in EdTech industry ($340B market)

---

## 🎥 Demo Video Structure (3 minutes)

### 0:00-0:30 - Hook & Problem
- "Education fails when it treats everyone the same"
- Show frustration of traditional learning tools
- Introduce NeuralSync Live

### 0:30-2:00 - Product Demonstration
- **Video Mode:** Upload TED talk → interactive questions appear
- **Problem Mode:** Photo of equation → step-by-step Socratic guidance
- **Document Mode:** PDF → concept map generation
- **Creative Mode:** Design sketch → expert feedback

### 2:00-2:45 - Impact & Vision
- Show session statistics and progress tracking
- Demonstrate adaptive difficulty in action
- Explain real-world applications (schools, self-learners, professionals)

### 2:45-3:00 - Call to Action
- "The future of learning is adaptive"
- Project repository and demo links
- Invitation to try NeuralSync Live

---

## 🛣️ Future Roadmap

- [ ] **Voice interaction** using Gemini's audio capabilities
- [ ] **Collaborative learning** - study groups with AI facilitator
- [ ] **Progress persistence** - cross-device sync
- [ ] **Teacher dashboard** for classroom integration
- [ ] **Mobile apps** (iOS & Android)
- [ ] **LMS integration** (Canvas, Moodle, etc.)
- [ ] **API for third-party** integrations
- [ ] **Multi-language** support (detect & adapt)

---

## 📝 Project Submission Details

### Description (~200 words)
**NeuralSync Live** transforms passive learning into active, personalized experiences using Gemini 3's multimodal AI. The platform offers four learning modes:

1. **Learn While You Watch** - Analyzes educational videos and generates context-aware questions at key moments
2. **Visual Problem Solver** - Uses image recognition to solve problems step-by-step with Socratic guidance  
3. **Document Intelligence** - Converts dense documents into interactive concept maps and adaptive quizzes
4. **Creative Workshop** - Provides expert design feedback and improvement suggestions

**Gemini 3 integration is central** to every feature. We leverage its vision capabilities for video/image analysis, reasoning for step-by-step problem solving, and generative abilities for creating questions, hints, and practice exercises. The platform uses **Gemini 2.0 Flash Exp** for low-latency interactions, with streaming responses for real-time chat.

The **adaptive difficulty system** analyzes user responses and adjusts question complexity in real-time. Rather than providing direct answers, the AI acts as a **Socratic tutor**, guiding learners to discover solutions themselves - a proven pedagogical approach now powered by state-of-the-art AI.

Built with Django backend and modern frontend, NeuralSync Live demonstrates Gemini 3's potential to revolutionize education through truly personalized, adaptive learning experiences.

### Links
- **Public Demo:** [Deploy to Vercel/Railway/PythonAnywhere]
- **Code Repository:** https://github.com/yourusername/neuralsync-live
- **Demo Video:** [Upload to YouTube]

---

## 👥 Team & Credits

**Created for:** Gemini 3 Global Hackathon  
**Built with:** ❤️ and lots of ☕  
**Powered by:** Google Gemini 3 AI

---

## 📄 License

This project is created for the Gemini 3 Hackathon.

---

## 🙏 Acknowledgments

- **Google DeepMind** for Gemini 3 API access
- **Gemini 3 Hackathon** organizers for the opportunity
- The amazing **AI/ML community** for inspiration

---

<div align="center">

### ⭐ If you like this project, please star it on GitHub! ⭐

**Built with Gemini 3 | Made for the Future of Learning**

</div>
