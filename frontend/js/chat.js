/**
 * 채팅 기능 모듈
 * 덱스 로봇과의 대화 인터페이스를 담당합니다.
 */

class DeksChat {
    constructor() {
        this.isTyping = false;
        this.chatHistory = [];
        this.currentSessionId = null;
        this.initializeElements();
        this.bindEvents();
        this.loadChatHistory();
    }

    /**
     * DOM 요소 초기화
     */
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatSendBtn = document.getElementById('chatSendBtn');
        this.clearChatBtn = document.getElementById('clearChat');
        this.chatModeBtn = document.getElementById('chatMode');
        this.commandModeBtn = document.getElementById('commandMode');
        this.chatModeContent = document.getElementById('chatModeContent');
        this.commandModeContent = document.getElementById('commandModeContent');
        this.commandHistory = document.getElementById('commandHistory');
        this.suggestionTags = document.querySelectorAll('.suggestion-tag');
    }

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 메시지 전송
        this.chatSendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 채팅 제어
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        
        // 모드 전환
        this.chatModeBtn.addEventListener('click', () => this.switchMode('chat'));
        this.commandModeBtn.addEventListener('click', () => this.switchMode('command'));

        // 추천 메시지 클릭
        this.suggestionTags.forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                const message = suggestion.getAttribute('data-message');
                this.chatInput.value = message;
                this.sendMessage();
            });
        });

        // 입력 필드 포커스
        this.chatInput.addEventListener('focus', () => {
            this.scrollToBottom();
        });
    }

    /**
     * 메시지 전송
     */
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isTyping) return;

        // 사용자 메시지 표시
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        this.setTyping(true);

        try {
            // API 호출
            const response = await window.deksAPI.sendChatMessage(message, this.currentSessionId);
            
            // 세션 ID 업데이트
            if (response.session_id) {
                this.currentSessionId = response.session_id;
            }

            // 봇 응답 표시
            this.addMessage(response.response, 'bot', {
                emotion: response.emotion,
                conversationType: response.conversation_type,
                nlpAnalysis: response.nlp_analysis
            });

            // 감정 상태에 따른 LED/버저 제어
            if (response.emotion) {
                this.handleEmotionResponse(response.emotion);
            }

            // 학습 데이터 제출
            this.submitLearningData({
                user_message: message,
                bot_response: response.response,
                emotion: response.emotion,
                intent: response.nlp_analysis?.intent,
                satisfaction: null // 사용자가 나중에 평가할 수 있도록
            });

        } catch (error) {
            console.error('채팅 메시지 전송 실패:', error);
            this.addMessage('죄송해요. 잠시 문제가 발생했어요. 다시 시도해 주세요.', 'bot');
            this.showToast('메시지 전송에 실패했습니다.', 'error');
        } finally {
            this.setTyping(false);
        }
    }

    /**
     * 메시지 추가
     */
    addMessage(text, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const time = new Date().toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const avatarIcon = sender === 'bot' ? 'fas fa-robot' : 'fas fa-user';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(text)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        // 메타데이터가 있으면 추가 정보 표시
        if (metadata.nlpAnalysis) {
            this.addNLPInfo(messageDiv, metadata.nlpAnalysis);
        }

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // 채팅 기록에 추가
        this.chatHistory.push({
            text,
            sender,
            timestamp: new Date().toISOString(),
            metadata
        });

        // 명령인 경우 명령 기록에도 추가
        if (sender === 'user' && this.isCommand(text)) {
            this.addCommandToHistory(text);
        }
    }

    /**
     * NLP 분석 정보 추가
     */
    addNLPInfo(messageDiv, nlpAnalysis) {
        if (!nlpAnalysis) return;

        const nlpInfo = document.createElement('div');
        nlpInfo.className = 'nlp-info';
        nlpInfo.style.cssText = `
            font-size: 0.7rem;
            color: #666;
            margin-top: 0.25rem;
            padding: 0.25rem 0.5rem;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 8px;
            border-left: 3px solid #667eea;
        `;

        const info = [];
        if (nlpAnalysis.intent) info.push(`의도: ${nlpAnalysis.intent}`);
        if (nlpAnalysis.emotion) info.push(`감정: ${nlpAnalysis.emotion}`);
        if (nlpAnalysis.keywords && nlpAnalysis.keywords.length > 0) {
            info.push(`키워드: ${nlpAnalysis.keywords.slice(0, 3).join(', ')}`);
        }

        nlpInfo.textContent = info.join(' | ');
        messageDiv.querySelector('.message-content').appendChild(nlpInfo);
    }

    /**
     * 타이핑 상태 설정
     */
    setTyping(isTyping) {
        this.isTyping = isTyping;
        this.chatSendBtn.disabled = isTyping;

        if (isTyping) {
            this.showTypingIndicator();
        } else {
            this.hideTypingIndicator();
        }
    }

    /**
     * 타이핑 인디케이터 표시
     */
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    /**
     * 타이핑 인디케이터 숨기기
     */
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /**
     * 감정 응답 처리
     */
    async handleEmotionResponse(emotion) {
        try {
            // LED 표정 설정
            const ledExpressions = {
                'happy': 'happy',
                'excited': 'happy',
                'proud': 'happy',
                'curious': 'neutral',
                'confused': 'neutral',
                'bittersweet': 'sad',
                'helpful': 'neutral'
            };

            const ledExpression = ledExpressions[emotion] || 'neutral';
            await window.deksAPI.setLEDExpression(ledExpression, 2000);

            // 버저 소리 설정
            const buzzerSounds = {
                'happy': 'success',
                'excited': 'success',
                'proud': 'success',
                'curious': 'info',
                'confused': 'error',
                'bittersweet': 'farewell',
                'helpful': 'info'
            };

            const buzzerSound = buzzerSounds[emotion] || 'info';
            await window.deksAPI.setBuzzerSound(buzzerSound, 1000, 300);

        } catch (error) {
            console.error('감정 응답 처리 실패:', error);
        }
    }

    /**
     * 채팅 기록 지우기
     */
    clearChat() {
        if (confirm('대화 기록을 모두 지우시겠습니까?')) {
            this.chatMessages.innerHTML = `
                <div class="message bot-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">안녕하세요! 저는 덱스 로봇이에요. 무엇을 도와드릴까요?</div>
                        <div class="message-time">방금 전</div>
                    </div>
                </div>
            `;
            this.chatHistory = [];
            this.currentSessionId = null;
            this.showToast('대화 기록이 지워졌습니다.', 'success');
        }
    }

    /**
     * 모드 전환
     */
    switchMode(mode) {
        // 버튼 상태 업데이트
        this.chatModeBtn.classList.toggle('active', mode === 'chat');
        this.commandModeBtn.classList.toggle('active', mode === 'command');
        
        // 콘텐츠 표시/숨김
        this.chatModeContent.classList.toggle('active', mode === 'chat');
        this.commandModeContent.classList.toggle('active', mode === 'command');
        
        // 입력 필드 플레이스홀더 업데이트
        if (mode === 'chat') {
            this.chatInput.placeholder = '덱스에게 메시지를 보내거나 명령을 내려주세요...';
        } else {
            this.chatInput.placeholder = '덱스에게 명령을 내려주세요...';
        }
        
        // 채팅 모드로 전환 시 스크롤
        if (mode === 'chat') {
            this.scrollToBottom();
        }
    }

    /**
     * 채팅 기록 로드
     */
    async loadChatHistory() {
        try {
            const response = await window.deksAPI.getChatHistory(this.currentSessionId, 20);
            if (response.success && response.conversations.length > 0) {
                // 기존 메시지 제거 (환영 메시지 제외)
                this.chatMessages.innerHTML = '';
                
                // 기록된 대화 표시
                response.conversations.forEach(conv => {
                    this.addMessage(conv.user_message, 'user');
                    this.addMessage(conv.bot_response, 'bot', {
                        emotion: conv.emotion,
                        conversationType: conv.conversation_type
                    });
                });
                
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('채팅 기록 로드 실패:', error);
        }
    }

    /**
     * 학습 데이터 제출
     */
    async submitLearningData(data) {
        try {
            await window.deksAPI.submitLearningData(data);
        } catch (error) {
            console.error('학습 데이터 제출 실패:', error);
        }
    }

    /**
     * 스크롤을 맨 아래로
     */
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    /**
     * HTML 이스케이프
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 명령인지 확인
     */
    isCommand(text) {
        const commandKeywords = [
            '앞으로', '뒤로', '왼쪽', '오른쪽', '돌아', '정지', '멈춰', '빙글빙글',
            '이동', '가줘', '돌아줘', '멈춰줘', '정지해줘', '움직여', '회전'
        ];
        
        return commandKeywords.some(keyword => text.includes(keyword));
    }

    /**
     * 명령 기록에 추가
     */
    addCommandToHistory(command) {
        const historyList = this.commandHistory.querySelector('.history-list');
        const time = new Date().toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <span class="history-command">${this.escapeHtml(command)}</span>
            <span class="history-time">${time}</span>
        `;

        // 최신 명령을 맨 위에 추가
        historyList.insertBefore(historyItem, historyList.firstChild);

        // 최대 10개까지만 유지
        const items = historyList.querySelectorAll('.history-item');
        if (items.length > 10) {
            historyList.removeChild(items[items.length - 1]);
        }
    }

    /**
     * 토스트 메시지 표시
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        const container = document.getElementById('toastContainer');
        container.appendChild(toast);
        
        // 애니메이션
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => container.removeChild(toast), 300);
        }, 3000);
    }
}

// 페이지 로드 시 채팅 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.deksChat = new DeksChat();
});
