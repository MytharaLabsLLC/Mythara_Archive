/**
 * MytharaConnect Chat Widget - Enterprise Grade
 * 
 * Copyright © 2025 Herbert Velez Jr. All rights reserved.
 * 
 * Best-in-class chat widget for Global Governance positioning
 * - Comprehensive error handling
 * - Fast client-side responses
 * - Mobile-responsive
 * - Industry-aware conversations
 * - Seamless pricing tier integration
 */

class MytharaWidget {
    constructor() {
        // DOM elements
        this.chatBubble = document.getElementById('chat-bubble');
        this.chatWindow = document.getElementById('chat-window');
        this.chatClose = document.getElementById('chat-close');
        this.chatInput = document.getElementById('chat-input');
        this.chatSend = document.getElementById('chat-send');
        this.chatMessages = document.getElementById('chat-messages');
        this.voiceBtn = document.getElementById('voice-btn');
        this.quickRepliesContainer = document.getElementById('quick-replies');
        this.progressTracker = document.getElementById('progress-tracker');
        this.tpmoCheckbox = document.getElementById('tpmo-checkbox');
        
        // State
        this.conversationStage = 0;
        this.engagementScore = 0;
        this.sessionStartTime = Date.now();
        this.lastInteractionTime = Date.now();
        this.hasUnread = false;
        this.isTyping = false;
        this.exitIntentShown = false;
        this.userLanguage = 'en';
        
        // Speech recognition
        this.recognition = null;
        this.voicesLoaded = false;
        this.selectedVoice = null;
        this.voiceChosen = false;
        
        // Initialize
        this.init();
    }
    
    init() {
        this.setupSpeechRecognition();
        this.setupEventListeners();
        this.setupEngagementTracking();
        this.loadVoices();
        
        // Prevent duplicate initialization
        if (this.chatBubble.dataset.initialized) return;
        this.chatBubble.dataset.initialized = 'true';
    }
    
    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported');
            this.voiceBtn.style.display = 'none';
            return;
        }
        
        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.chatInput.value = transcript;
                this.voiceBtn.classList.remove('listening');
                this.handleSend();
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.voiceBtn.classList.remove('listening');
                
                if (event.error === 'not-allowed') {
                    this.addMessage('Microphone access denied. Please enable it in your browser settings.', false);
                }
            };
            
            this.recognition.onend = () => {
                this.voiceBtn.classList.remove('listening');
            };
        } catch (error) {
            console.error('Failed to initialize speech recognition:', error);
            this.voiceBtn.style.display = 'none';
        }
    }
    
    loadVoices() {
        if (!('speechSynthesis' in window)) {
            console.warn('Speech synthesis not supported');
            return;
        }
        
        try {
            speechSynthesis.onvoiceschanged = () => {
                this.voicesLoaded = true;
            };
        } catch (error) {
            console.error('Failed to load voices:', error);
        }
    }
    
    setupEventListeners() {
        // Chat bubble - open widget
        this.chatBubble.addEventListener('click', () => {
            this.openChat();
        });
        
        // Close button
        this.chatClose.addEventListener('click', () => {
            this.closeChat();
        });
        
        // Send button
        this.chatSend.addEventListener('click', () => {
            this.handleSend();
        });
        
        // Enter key in input
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });
        
        // Voice button
        if (this.voiceBtn) {
            this.voiceBtn.addEventListener('click', () => {
                this.handleVoiceInput();
            });
        }
        
        // TPMO checkbox - enable/disable input
        if (this.tpmoCheckbox) {
            // Disable input initially
            this.chatInput.disabled = true;
            this.chatSend.disabled = true;
            this.chatInput.placeholder = 'Please acknowledge TPMO terms to chat...';
            
            this.tpmoCheckbox.addEventListener('change', () => {
                if (this.tpmoCheckbox.checked) {
                    this.chatInput.disabled = false;
                    this.chatSend.disabled = false;
                    this.chatInput.placeholder = 'Ask me anything about Mythara...';
                    this.chatInput.focus();
                } else {
                    this.chatInput.disabled = true;
                    this.chatSend.disabled = true;
                    this.chatInput.placeholder = 'Please acknowledge TPMO terms to chat...';
                }
            });
        }
        
        // Window close - cleanup
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }
    
    setupEngagementTracking() {
        let scrollDepth = 0;
        let idleTimer = null;
        
        // Track scroll depth
        window.addEventListener('scroll', () => {
            const currentScroll = window.scrollY / (document.body.scrollHeight - window.innerHeight) * 100;
            if (currentScroll > scrollDepth) {
                scrollDepth = currentScroll;
            }
        });
        
        // Track user activity
        const resetIdle = () => {
            this.lastInteractionTime = Date.now();
            
            if (idleTimer) clearTimeout(idleTimer);
            
            idleTimer = setTimeout(() => {
                const idleTime = (Date.now() - this.lastInteractionTime) / 1000;
                
                if (idleTime > 45 && this.chatWindow.classList.contains('active')) {
                    this.showTypingIndicator();
                    setTimeout(() => {
                        this.hideTypingIndicator();
                        this.addMessage("I'm here if you have questions. No pressure.");
                        this.clearQuickReplies();
                    }, 1000);
                }
            }, 30000);
        };
        
        document.addEventListener('mousemove', resetIdle);
        document.addEventListener('keydown', resetIdle);
        resetIdle();
        
        // Exit intent - gentle reminder only
        document.addEventListener('mouseleave', (e) => {
            if (e.clientY <= 0 && !this.exitIntentShown && this.conversationStage < 3) {
                this.exitIntentShown = true;
                if (!this.chatWindow.classList.contains('active')) {
                    this.setUnreadNotification(true);
                }
            }
        });
    }
    
    openChat() {
        this.chatWindow.classList.add('active');
        this.setUnreadNotification(false);
        this.engagementScore += 10;
        
        // Always start fresh conversation when opening
        if (this.chatMessages.children.length === 0 || !this.voiceChosen) {
            this.startConversation();
        }
        
        // Focus input
        this.chatInput.focus();
    }
    
    closeChat() {
        this.chatWindow.classList.remove('active');
        this.stopSpeech();
        
        // Mark for reset on next open
        this.voiceChosen = false;
        this.selectedVoice = null;
        this.conversationStage = 0;
        
        // Clear everything
        this.chatMessages.innerHTML = '';
        this.clearQuickReplies();
        this.updateProgress(0);
    }
    
    startConversation() {
        this.conversationStage = 0;
        this.updateProgress(0);
        
        // Auto-detect language and select appropriate voice
        this.autoSelectVoice();
        
        // Get agent name from selected voice
        const agentName = this.getAgentName();
        
        this.showTypingIndicator();
        setTimeout(() => {
            this.hideTypingIndicator();
            this.addMessage(`Hey there! I'm ${agentName}. I'm here to help you learn about Mythara's Soul Cradle and Global Governance—tools that make AI safety easier. What questions can I answer for you?`, false);
            
            // Add subtle note about rotating representatives and nonprofit pricing
            setTimeout(() => {
                this.addMessage(`<em style="font-size: 0.85em; opacity: 0.7;">We have representatives around the globe, so you'll always have someone to talk to. Nonprofits doing good work? Ask about special pricing!</em>`, false);
            }, 400);
            
            this.addQuickReplies(['What is Soul Cradle?', 'Show pricing', 'Nonprofit pricing?']);
        }, 800);
    }
    
    getAgentName() {
        if (!this.selectedVoice) return 'Alex';
        
        const voiceName = this.selectedVoice.name;
        
        // Extract first name from voice name (e.g., "Microsoft Zira Desktop" -> "Zira")
        if (voiceName.includes('Zira')) return 'Zira';
        if (voiceName.includes('Samantha')) return 'Samantha';
        if (voiceName.includes('Karen')) return 'Karen';
        if (voiceName.includes('David')) return 'David';
        if (voiceName.includes('Mark')) return 'Mark';
        if (voiceName.includes('James')) return 'James';
        if (voiceName.includes('Susan')) return 'Susan';
        if (voiceName.includes('Victoria')) return 'Victoria';
        if (voiceName.includes('Daniel')) return 'Daniel';
        
        // Language-based names
        if (this.selectedVoice.lang.startsWith('es')) return 'Sofia';
        if (this.selectedVoice.lang.startsWith('fr')) return 'Amélie';
        if (this.selectedVoice.lang.startsWith('zh')) return 'Wei';
        if (this.selectedVoice.lang.startsWith('ja')) return 'Yuki';
        if (this.selectedVoice.lang.startsWith('en-IN')) return 'Priya';
        
        // Gender-based fallback
        if (voiceName.toLowerCase().includes('female')) return 'Maya';
        if (voiceName.toLowerCase().includes('male')) return 'Alex';
        
        return 'Jordan'; // Gender-neutral fallback
    }
    
    autoSelectVoice() {
        this.voiceChosen = true;
        const voices = speechSynthesis.getVoices();
        
        // Detect user's language from browser
        const userLang = navigator.language || navigator.userLanguage || 'en-US';
        console.log('User language detected:', userLang);
        
        // Build voice pool that matches user's language
        let voicePool = [];
        
        // Match voices to user's language
        if (userLang.startsWith('en')) {
            // English speakers get English voices
            voicePool = voices.filter(v => v.lang.startsWith('en'));
        } else if (userLang.startsWith('es')) {
            // Spanish speakers get Spanish voices
            voicePool = voices.filter(v => v.lang.startsWith('es'));
        } else if (userLang.startsWith('fr')) {
            // French speakers get French voices
            voicePool = voices.filter(v => v.lang.startsWith('fr'));
        } else if (userLang.startsWith('zh')) {
            // Chinese speakers get Chinese voices
            voicePool = voices.filter(v => v.lang.startsWith('zh'));
        } else if (userLang.startsWith('ja')) {
            // Japanese speakers get Japanese voices
            voicePool = voices.filter(v => v.lang.startsWith('ja'));
        } else if (userLang.startsWith('de')) {
            // German speakers get German voices
            voicePool = voices.filter(v => v.lang.startsWith('de'));
        } else if (userLang.startsWith('hi')) {
            // Hindi speakers get Hindi/Indian voices
            voicePool = voices.filter(v => v.lang.startsWith('hi') || v.lang === 'en-IN');
        } else {
            // Fallback to English for unsupported languages
            voicePool = voices.filter(v => v.lang.startsWith('en'));
        }
        
        // Randomly select from the language-matched pool
        if (voicePool.length > 0) {
            this.selectedVoice = voicePool[Math.floor(Math.random() * voicePool.length)];
            console.log('Selected voice:', this.selectedVoice.name, '(' + this.selectedVoice.lang + ')');
        } else {
            this.selectedVoice = null;
            console.log('No voices available for', userLang, '- text only mode');
        }
    }
    
    handleSend() {
        const text = this.chatInput.value.trim();
        if (!text || this.isTyping) return;
        
        // Stop any ongoing speech when user sends a message
        this.stopSpeech();
        
        this.addMessage(text, true);
        this.chatInput.value = '';
        this.clearQuickReplies();
        this.lastInteractionTime = Date.now();
        this.engagementScore += 5;
        
        // Get response
        this.isTyping = true;
        this.showTypingIndicator();
        
        // Natural delay (500-1000ms)
        const delay = 500 + Math.random() * 500;
        setTimeout(() => {
            this.hideTypingIndicator();
            const response = this.getResponse(text);
            this.addMessage(response);
            this.isTyping = false;
            
            // Update progress
            const progressMap = { 0: 0, 1: 25, 2: 50, 3: 75, 4: 100 };
            this.updateProgress(progressMap[this.conversationStage] || 0);
            
            // Suggest next step
            setTimeout(() => {
                this.suggestNextStep(text);
            }, 1500);
        }, delay);
    }
    
    handleVoiceInput() {
        if (!this.recognition) {
            this.addMessage('Voice input is not supported in this browser. Please use Chrome, Edge, or Safari.');
            return;
        }
        
        // Stop any ongoing speech when user clicks microphone
        this.stopSpeech();
        
        if (this.voiceBtn.classList.contains('listening')) {
            this.recognition.stop();
            this.voiceBtn.classList.remove('listening');
        } else {
            try {
                this.voiceBtn.classList.add('listening');
                this.recognition.start();
            } catch (error) {
                console.error('Failed to start speech recognition:', error);
                this.voiceBtn.classList.remove('listening');
                this.addMessage('Failed to start voice input. Please try again.');
            }
        }
    }
    
    getResponse(message) {
        const lowerInput = message.toLowerCase();
        this.conversationStage = Math.min(this.conversationStage + 1, 4);
        
        // Global Governance / What is Mythara
        if (lowerInput.includes('what is') || lowerInput.includes('mythara') || lowerInput.includes('governance')) {
            return "Mythara Engine protects your AI from manipulation and keeps it compliant. We catch adversarial attacks and emotional manipulation patterns before they cause problems. Most small businesses start with our Startup Small Teams tier at 249 per month to validate their system, then scale up as they grow. Which tier makes sense for your stage?";
        }
        
            // Pricing / Cost
            if (lowerInput.includes('pricing') || lowerInput.includes('cost') || lowerInput.includes('price') || lowerInput.includes('how much')) {
                return "We have tiers for every stage. Startup Small Teams is 249 per month, perfect for small businesses with 1 to 10 employees. If you're an early stage AI company, the Startup License at 2500 per month gives you 100 thousand API calls. Growing companies at 5 to 50 million ARR typically choose our Growth License at 10 thousand per month. Which stage is your company at?";
            }        // 34 frameworks
        if (lowerInput.includes('framework') || lowerInput.includes('regulation') || lowerInput.includes('compliance') || lowerInput.includes('34')) {
            return "We validate against 34 regulatory frameworks including HIPAA, GDPR, FINRA, FDA, and the EU AI Act. Your industry likely has 5 to 10 that apply. Most small teams start with our Startup Small Teams tier at 249 per month for initial validation. Should I send you the integration docs to get started?";
        }
        
        // Adversarial hardening / Security
        if (lowerInput.includes('adversarial') || lowerInput.includes('security') || lowerInput.includes('attack') || lowerInput.includes('loophole')) {
            return "We catch hidden characters, homoglyph attacks, prompt injections, and data exfiltration attempts. Every validation gets cryptographically signed for audit trails. Most teams integrate this in a few hours. Want me to have our team reach out about your specific security needs?";
        }
        
        // Legal indemnification
        if (lowerInput.includes('indemnif') || lowerInput.includes('legal') || lowerInput.includes('liability') || lowerInput.includes('coverage')) {
            return "No indemnification is currently offered on any tier. Can I help you compare tiers on features, support, or compliance coverage instead?";
        }
        
        // ROI / Business case
        if (lowerInput.includes('roi') || lowerInput.includes('return') || lowerInput.includes('save') || lowerInput.includes('business case')) {
            return "A single GDPR fine can reach 20 million euros or more. One FDA warning letter can delay your launch 6 to 12 months. Our Startup Small Teams tier starts at 249 per month. Most teams see positive ROI within the first month by avoiding just one compliance issue. Want me to send you our ROI calculator?";
        }
        
        // How it works / Technical
        if (lowerInput.includes('how') || lowerInput.includes('technical') || lowerInput.includes('api') || lowerInput.includes('integrate')) {
            return "REST API with JSON. Most teams integrate in a few hours using our SDK. We provide sandbox keys for testing. Should I email you the API documentation and a sandbox key to start testing today?";
        }
        
        // Industries
        if (lowerInput.includes('industry') || lowerInput.includes('who uses') || lowerInput.includes('healthcare') || lowerInput.includes('finance')) {
            return "The system is built for regulated industries like healthcare AI (HIPAA), financial services (FINRA), pharma (FDA), and defense (ITAR). Each industry has specific compliance requirements it is designed to address. Which industry describes your AI application best?";
        }
        
        // Competition / Alternatives
        if (lowerInput.includes('competitor') || lowerInput.includes('alternative') || lowerInput.includes('versus') || lowerInput.includes('compare')) {
            return "You could definitely build something yourself or use other compliance tools. Main difference with us is we specifically focus on AI safety and manipulation detection, which isn't something most tools do. But yeah, there are other options out there—happy to talk through what makes sense for your situation.";
        }
        
        // Implementation / Onboarding
        if (lowerInput.includes('implement') || lowerInput.includes('onboard') || lowerInput.includes('getting started') || lowerInput.includes('setup')) {
            return "Getting started is pretty easy. For Startup Small Teams and Startup License tiers, you basically just sign up and start using the API—most people are up and running same day. Higher tiers like Growth and Enterprise we do a kickoff call, help you integrate it properly, and make sure everything's working how you need it. Usually takes a few days to a week depending on your setup.";
        }
        
        // Support
        if (lowerInput.includes('support') || lowerInput.includes('help') || lowerInput.includes('assistance')) {
            return "Startup tiers get email support with same day response. Professional and Growth License get priority support with 12 hour response. Enterprise gets 24 7 premium support with 2 hour response if something breaks at 3am. We try to be pretty responsive—compliance stuff can be time-sensitive.";
        }
        
        // Data privacy / Security
        if (lowerInput.includes('privacy') || lowerInput.includes('data') || lowerInput.includes('encryption')) {
            return "Your data stays yours—we don't sell it or do anything weird with it. Everything's encrypted, and we're building to SOC 2 standards. You can see the full security details at mythara.ai/security if you want to dig into the technical stuff.";
        }
        
        // Contract / Terms
        if (lowerInput.includes('contract') || lowerInput.includes('commitment') || lowerInput.includes('term') || lowerInput.includes('cancel')) {
            return "We do monthly or annual contracts. If you want to cancel, just give us 30 days notice—no tricks or hidden fees. If you want to upgrade partway through, we'll credit what you already paid. Trying to keep it simple and fair.";
        }
        
        // Proof / Case studies
        if (lowerInput.includes('proof') || lowerInput.includes('case study') || lowerInput.includes('customer') || lowerInput.includes('reference')) {
            return "We've tested the system pretty extensively—you can see the test results in our repo. We run an early-access program, but we don't name participants publicly. If you want to talk specifics or get a reference conversation set up, email Mythara.Engine@yahoo.com and we can figure something out.";
        }
        
        // Startup specific
        if (lowerInput.includes('startup') || lowerInput.includes('small') || lowerInput.includes('seed')) {
            return "We have startup-friendly options for small teams and early-stage AI companies — scope and pricing depend on your stage and use. Email Mythara.Engine@yahoo.com and we'll figure out what fits.";
        }
        
        // Enterprise specific
        if (lowerInput.includes('enterprise') && !lowerInput.includes('license')) {
            return "We offer an enterprise tier for larger organizations — custom scope, dedicated support, and deployment options including on-premise. Pricing is set per engagement. Email Mythara.Engine@yahoo.com and we'll walk through what fits your scale.";
        }
        
        // On-premise specific
        if (lowerInput.includes('on-premise') || lowerInput.includes('air-gapped') || lowerInput.includes('government')) {
            return "If you need everything running on your own infrastructure—like government or defense work where cloud isn't an option—we can do that. It's a bigger setup and costs more, but you get full control. Email us if that's what you need and we can talk through the details.";
        }
        
        // Employee count detection
        const employeeMatch = lowerInput.match(/(\d+)\s*(employee|people|person|team|staff|member)/i);
        if (employeeMatch) {
            const count = parseInt(employeeMatch[1]);
            if (count <= 10) {
                return "Perfect! With " + count + " employees, Startup Small Teams at 249 per month is your best fit. You get full Global Governance access and same day email support. How many AI agents or models do you need to govern?";
            } else if (count <= 50) {
                return "With " + count + " employees, you'd want our Professional Growing Teams tier at 999 per month. You get priority support with 12 hour response, advanced analytics, and dedicated onboarding. How many AI agents or models do you need to govern?";
            } else {
                return "With " + count + " employees, you're looking at either Growth License at 10 thousand per month or Enterprise License at 50 thousand per month, depending on your API volume and compliance needs. How many AI agents or models do you need to govern?";
            }
        }
        
        // AI agent/model count detection
        const agentMatch = lowerInput.match(/(\d+)\s*(agent|model|bot|ai|system|assistant)/i);
        if (agentMatch) {
            const count = parseInt(agentMatch[1]);
            if (count === 0) {
                return "Ah, so you're in the planning phase—that's actually the perfect time to think about governance. A lot of companies wait until after they deploy and then realize they have compliance gaps. Are you building AI in house, or integrating third party models like GPT or Claude?";
            } else if (count === 1) {
                return "Just one AI agent is perfect for starting out. Our Startup Small Teams tier at 249 per month handles single agent deployments easily. You get 100 validations per day included. Should I send you the API docs to get started?";
            } else if (count <= 5) {
                return count + " AI agents—that's a solid setup. Our Startup License or Professional tier can handle that volume. The Startup License at 2500 per month gives you 100 thousand API calls which covers multiple agents nicely. Want to see the integration guide?";
            } else if (count <= 20) {
                return count + " AI agents means you need serious API volume. Growth License at 10 thousand per month gives you 1 million API calls per month and unlimited environments. That should cover your multi agent architecture. Should I connect you with our team?";
            } else {
                return count + " AI agents is enterprise scale. You'll want our Enterprise License at 50 thousand per month with unlimited API calls and dedicated support. At that scale, compliance gets complex fast. Want to schedule a call with our enterprise team?";
            }
        }
        
        // Planning stage detection (no agents yet)
        if ((lowerInput.includes('none') || lowerInput.includes('zero') || lowerInput.includes('not yet') || lowerInput.includes('planning')) && 
            (lowerInput.includes('agent') || lowerInput.includes('ai') || lowerInput.includes('model'))) {
            return "Perfect timing—planning governance before you deploy is way smarter than scrambling after launch. Are you building AI in house, or planning to use third party models like GPT, Claude, or Gemini?";
        }
        
        // ARR / Revenue detection
        const revenueMatch = lowerInput.match(/(\d+)\s*(million|m|k|thousand)/i);
        if (revenueMatch && (lowerInput.includes('revenue') || lowerInput.includes('arr') || lowerInput.includes('making'))) {
            const amount = parseFloat(revenueMatch[1]);
            const unit = revenueMatch[2].toLowerCase();
            const millions = unit.startsWith('m') ? amount : amount / 1000;
            
            if (millions < 5) {
                return "Under 5 million ARR, the Startup License at 2500 per month is perfect. You get 100 thousand API calls per month and 5 production environments. Should I send you the onboarding details?";
            } else if (millions < 50) {
                return "At your revenue level, Growth License at 10 thousand per month makes sense. You get 1 million API calls per month, unlimited users, and priority support. Want to schedule a demo?";
            } else {
                return "At your scale, Enterprise License at 50 thousand per month is the right fit. You get unlimited API calls and 24 7 premium support. Should I have our enterprise team reach out?";
            }
        }
        
        // Email address detection
        const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
        if (emailPattern.test(lowerInput)) {
            return "Perfect! I've got your email. Someone from our team will reach out within 24 hours with everything you need to get started. Looking forward to working with you!";
        }
        
        // Yes/No responses
        if (lowerInput.includes('yes') || lowerInput.includes('sure') || lowerInput.includes('okay') || lowerInput.includes('ok')) {
            return "Great! Email me at Mythara.Engine@yahoo.com and I'll send you everything you need. What's the best email address to reach you?";
        }
        
        if (lowerInput.includes('no') || lowerInput.includes('not interested') || lowerInput.includes('no thanks')) {
            return "No problem! Is there anything else I can help you with? Feel free to ask about pricing, features, or how it works?";
        }
        
        // Default fallback
        if (lowerInput.length < 3) {
            return "I need a bit more context. What are you curious about? Pricing? How it works? Something else?";
        }
        
        // Intelligent fallback
        if (lowerInput.includes('?')) {
            return "That's a good question. Let me connect you with someone who can give you a proper answer—email Mythara.Engine@yahoo.com and we'll get back to you same day.";
        }
        
        // Final fallback
        return "Hmm, not totally sure what you're asking. Can you rephrase that? Or ask me something like: what is this, how much does it cost, or how does it work?";
    }
    
    suggestNextStep(userInput) {
        const lower = userInput.toLowerCase();
        
        // If they asked about governance, suggest pricing
        if (lower.includes('governance') || lower.includes('what is') && this.conversationStage < 3) {
            this.showTypingIndicator();
            setTimeout(() => {
                this.hideTypingIndicator();
                this.addMessage("Want to see pricing for your company size?");
                this.addQuickReplies(['Yes, show pricing', 'Tell me about frameworks', 'ROI examples']);
            }, 1000);
        }
        
        // If they asked about pricing, push to action
        else if ((lower.includes('pricing') || lower.includes('cost')) && this.conversationStage < 3) {
            this.showTypingIndicator();
            setTimeout(() => {
                this.hideTypingIndicator();
                this.addMessage("Which tier fits your current stage?");
                this.addQuickReplies(['Startup Small Teams', 'Startup License', 'Growth License']);
            }, 1000);
        }
        
        // If they asked about frameworks, push to ROI
        else if (lower.includes('framework') && this.conversationStage < 3) {
            this.showTypingIndicator();
            setTimeout(() => {
                this.hideTypingIndicator();
                this.addMessage("Want to see hypothetical ROI scenarios?");
                this.addQuickReplies(['Yes, show ROI', 'Show pricing', 'Technical details']);
            }, 1000);
        }
    }
    
    addMessage(text, isUser = false) {
        const msg = document.createElement('div');
        msg.className = `chat-message ${isUser ? 'user' : 'bot'}`;
        
        // Support HTML for formatting but sanitize user input
        if (text.includes('<') && !isUser) {
            msg.innerHTML = text;
        } else {
            msg.textContent = text;
        }
        
        this.chatMessages.appendChild(msg);
        this.scrollToBottom();
        
        // Speak bot messages (with error handling)
        if (!isUser) {
            this.speakMessage(text);
        }
    }
    
    speakMessage(text) {
        if (!('speechSynthesis' in window) || !this.voicesLoaded) return;
        
        try {
            // Clean text for natural speech
            const spokenText = text
                .replace(/<[^>]*>/g, '') // Remove HTML tags
                .replace(/\*\*/g, '') // Remove markdown bold
                .replace(/24\/7/g, '24 7') // Say "24 7" instead of "24/7"
                .replace(/\$/g, 'dollar ') // Say "dollar" instead of symbol
                .replace(/€/g, 'euro ') // Say "euro" instead of symbol
                .replace(/£/g, 'pound ') // Say "pound" instead of symbol
                .replace(/(\d+)x/gi, '$1 times') // Say "14 times" instead of "14x"
                .replace(/(\d+)K\s*-\s*(\d+)K/gi, '$1 thousand to $2 thousand') // "14K - 30K" -> "14 thousand to 30 thousand"
                .replace(/(\d+)M\s*-\s*(\d+)M/gi, '$1 million to $2 million') // "2M - 5M" -> "2 million to 5 million"
                .replace(/\d+K/g, (match) => match.replace('K', ' thousand'))
                .replace(/\d+M/g, (match) => match.replace('M', ' million'))
                .replace(/%/g, ' percent')
                .replace(/&/g, ' and ')
                .replace(/#/g, ' number ')
                .replace(/@/g, ' at ')
                .replace(/\+/g, ' plus ')
                .replace(/—/g, ', ') // Long dash = pause (comma)
                .replace(/–/g, ', ') // En dash = pause (comma)
                .replace(/ - /g, ' to ') // Say "to" instead of dash with spaces
                .replace(/-/g, ' ') // Remove remaining dashes (like tic-tac-toe)
                .replace(/\.\.\./g, ', ')
                .replace(/[^\w\s.,!?']/g, '') // Remove other special characters
                .substring(0, 300); // Limit length
            
            const utterance = new SpeechSynthesisUtterance(spokenText);
            
            // Use user-selected voice or skip if they chose text only
            if (this.selectedVoice === null && this.voiceChosen) {
                return; // User chose "Text only"
            }
            
            if (this.selectedVoice) {
                utterance.voice = this.selectedVoice;
                console.log('Using voice:', this.selectedVoice.name);
            }
            
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            
            utterance.onerror = (event) => {
                console.error('Speech synthesis error:', event.error);
            };
            
            speechSynthesis.speak(utterance);
        } catch (error) {
            console.error('Failed to speak message:', error);
        }
    }
    
    stopSpeech() {
        if ('speechSynthesis' in window) {
            try {
                speechSynthesis.cancel();
            } catch (error) {
                console.error('Failed to stop speech:', error);
            }
        }
    }
    
    showTypingIndicator() {
        if (document.getElementById('typing-indicator')) return;
        
        const typing = document.createElement('div');
        typing.className = 'chat-message bot typing-indicator';
        typing.id = 'typing-indicator';
        typing.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
        this.chatMessages.appendChild(typing);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }
    
    addQuickReplies(suggestions) {
        this.clearQuickReplies();
        
        suggestions.forEach(text => {
            const btn = document.createElement('button');
            btn.className = 'quick-reply';
            btn.textContent = text;
            btn.onclick = () => {
                this.chatInput.value = text;
                this.handleSend();
                this.clearQuickReplies();
            };
            this.quickRepliesContainer.appendChild(btn);
        });
    }
    
    clearQuickReplies() {
        this.quickRepliesContainer.innerHTML = '';
    }
    
    updateProgress(percentage) {
        if (this.progressTracker) {
            this.progressTracker.style.width = percentage + '%';
        }
    }
    
    setUnreadNotification(unread) {
        this.hasUnread = unread;
        if (unread) {
            this.chatBubble.classList.add('has-unread');
        } else {
            this.chatBubble.classList.remove('has-unread');
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    cleanup() {
        this.stopSpeech();
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (error) {
                console.error('Failed to stop recognition:', error);
            }
        }
    }
}

// Initialize widget when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new MytharaWidget();
    });
} else {
    new MytharaWidget();
}
