/* VANT AI Counselor - Modular Widget Script */

class ChatWidget {
    constructor() {
        this.container = document.getElementById('chat-window');
        this.bubble = document.getElementById('chat-bubble');
        this.input = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('chat-send');
        this.messagesContainer = document.getElementById('chat-messages');
        this.sessionId = localStorage.getItem('chat_session_id') || this.generateSessionId();

        this.init();
    }

    generateSessionId() {
        const id = 'session_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chat_session_id', id);
        return id;
    }

    init() {
        // Toggle Chat
        this.bubble.addEventListener('click', () => {
            const badge = document.getElementById('chat-badge');
            if (badge) badge.style.display = 'none'; // Hide badge when clicked
            this.bubble.style.animation = 'none'; // Stop bounce
            this.toggle();
        });

        // Send Message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Modal Close
        const modal = document.getElementById('course-modal');
        const closeBtn = document.querySelector('.close-modal');
        if (closeBtn) closeBtn.onclick = () => modal.style.display = 'none';
        window.onclick = (event) => {
            if (event.target == modal) modal.style.display = 'none';
        };

        // Add Close Button Events
        const chatCloseBtn = document.querySelector('.close-chat-btn');
        if (chatCloseBtn) chatCloseBtn.addEventListener('click', () => this.toggle(false));

        // Submit Intake Form
        const intakeForm = document.getElementById('intake-form');
        if (intakeForm) {
            intakeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const msg = document.getElementById('intake-msg').value.trim();

                // Switch Screens
                document.getElementById('chat-screen-intake').style.display = 'none';
                document.getElementById('chat-screen-active').style.display = 'flex';

                // Add Initial Bot Message matching original screenshot
                this.addMessage("Welcome to Linkcode Technologies. We are happy to help you.", 'bot');

                if (msg) {
                    this.sendMessage(msg);
                }
            });

            // Auto-notification after 5 seconds to grab user attention
            setTimeout(() => {
                if (!this.container.classList.contains('active')) {
                    const badge = document.getElementById('chat-badge');
                    if (badge) badge.style.display = 'block';
                    this.bubble.style.animation = 'chatBounce 2s ease 2';
                }
            }, 5000);
        }

        // Disable initial trigger since we do it on form submit now
        // this.addMessage("Hello! I'm your Linkcode Technologies Counselor. How can I help you today?", 'bot');
    }

    toggle(forceOpen = false) {
        if (forceOpen) {
            this.container.classList.add('active');
        } else {
            this.container.classList.toggle('active');
        }
    }

    addMessage(text, role) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.style.cssText = `
            padding: 12px 18px;
            border-radius: ${role === 'user' ? '18px 18px 4px 18px' : '4px 18px 18px 18px'};
            max-width: 80%;
            font-size: 0.95rem;
            margin-bottom: 2px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            ${role === 'user' ? 'align-self: flex-end; background: var(--chat-primary); color: white;' : 'align-self: flex-start; background: #ffffff; color: var(--text-main); border: 1px solid var(--glass-border);'}
            animation: fadeInUp 0.3s ease;
        `;

        // Add a subtle name label for user
        if (role === 'user') {
            const label = document.createElement('div');
            label.textContent = "you";
            label.style.cssText = 'align-self: flex-end; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 2px; margin-right: 5px;';
            this.messagesContainer.appendChild(label);
        }
        msgDiv.textContent = text;
        this.messagesContainer.appendChild(msgDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async sendMessage(prefillQuery = null) {
        const query = prefillQuery || this.input.value.trim();
        if (!query) return;

        if (!prefillQuery) this.input.value = '';
        this.addMessage(query, 'user');

        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'message bot loading';
        loadingMsg.textContent = 'Counselor is thinking...';
        loadingMsg.style.cssText = 'font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px;';
        this.messagesContainer.appendChild(loadingMsg);

        try {
            const response = await fetch('/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: query,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();
            this.messagesContainer.removeChild(loadingMsg);

            if (data.answer) {
                this.addMessage(data.answer, 'bot');
            } else {
                throw new Error('Empty response');
            }
        } catch (error) {
            console.error('Chat Error:', error);
            if (loadingMsg.parentNode) this.messagesContainer.removeChild(loadingMsg);
            this.addMessage("I'm sorry, I'm having trouble connecting to my brain right now. Please try again later.", 'bot');
        }
    }

    async fetchCourses() {
        try {
            const response = await fetch('/api/courses');
            const courses = await response.json();
            this.courses = courses; // Store globally
            this.renderCourses(courses);
        } catch (error) {
            console.error('Failed to fetch courses:', error);
        }
    }

    renderCourses(courses) {
        const container = document.getElementById('course-grid');
        if (!container) return;

        container.innerHTML = '';
        courses.forEach(course => {
            const card = document.createElement('div');
            card.className = 'glass';
            card.style.cssText = 'padding: 30px; border-radius: 20px; transition: var(--transition); border: 1px solid var(--glass-border); cursor: pointer;';
            card.onclick = () => this.showModal(course);

            card.innerHTML = `
                <div class="rating-stars">
                    ${this.renderStars(course.rating)}
                    <span class="rating-value">${course.rating}</span>
                </div>
                <i class="fas ${this.getCourseIcon(course.name)}" style="font-size: 2rem; color: var(--primary); margin-bottom: 20px;"></i>
                <h3 style="margin-bottom: 10px;">${course.name}</h3>
                <p style="color: var(--text-muted); margin-bottom: 15px; font-size: 0.9rem;">${course.duration_months} Months | Intensive Training</p>
                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--glass-border); padding-top: 15px; margin-top: 15px;">
                    <span style="font-size: 0.8rem; color: var(--primary); font-weight: 600;">LEARN MORE <i class="fas fa-arrow-right" style="font-size: 0.7rem; margin-left: 5px;"></i></span>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">${course.status}</span>
                </div>
            `;
            container.appendChild(card);
        });
    }

    showModal(course) {
        const modal = document.getElementById('course-modal');
        const body = document.getElementById('modal-body');

        body.innerHTML = `
            <h2>${course.name}</h2>
            <p class="modal-info-p">${course.description}</p>
            <div class="modal-features">
                <div class="feature-item"><i class="fas fa-check-circle" style="color: var(--primary);"></i> 100% Placement Support</div>
                <div class="feature-item"><i class="fas fa-check-circle" style="color: var(--primary);"></i> Industry Certifications</div>
                <div class="feature-item"><i class="fas fa-clock" style="color: var(--primary);"></i> ${course.duration_months} Months Duration</div>
                <div class="feature-item"><i class="fas fa-laptop-code" style="color: var(--primary);"></i> ${course.format} Mode</div>
            </div>
            <div style="display: flex; gap: 15px;">
                <button id="enroll-btn" class="btn-primary" style="border: none; cursor: pointer; flex: 1;">Enroll Now</button>
                <button onclick="document.getElementById('course-modal').style.display='none'" class="glass" style="flex: 1; padding: 10px; border-radius: 99px; color: var(--text-main); border: 1px solid var(--glass-border);">Close</button>
            </div>
        `;

        document.getElementById('enroll-btn').onclick = () => {
            modal.style.display = 'none';
            this.toggle(true);
            this.sendMessage(`I want to enroll in ${course.name}. Can you tell me the process and fees?`);
        };

        modal.style.display = 'flex';
    }

    renderStars(rating) {
        const stars = Math.floor(rating);
        let html = '';
        for (let i = 0; i < 5; i++) {
            html += `<i class="${i < stars ? 'fas' : 'far'} fa-star"></i>`;
        }
        return html;
    }

    getCourseIcon(name) {
        name = name.toLowerCase();
        if (name.includes('python')) return 'fa-code';
        if (name.includes('data') || name.includes('ai')) return 'fa-brain';
        if (name.includes('cyber')) return 'fa-shield-halved';
        if (name.includes('java')) return 'fa-coffee';
        if (name.includes('cloud')) return 'fa-cloud';
        return 'fa-laptop-code';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const chat = new ChatWidget();
    chat.fetchCourses(); // Load dynamic courses

    // Header scroll effect
    window.addEventListener('scroll', () => {
        const header = document.querySelector('header');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
});

