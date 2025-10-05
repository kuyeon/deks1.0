/**
 * API 통신 모듈
 * 백엔드 API와의 통신을 담당합니다.
 */

class DeksAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000/api/v1';
        this.userId = 'web_user_' + Date.now();
        this.sessionId = 'session_' + Date.now();
    }

    /**
     * HTTP 요청을 보내는 공통 메서드
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API 요청 실패:', error);
            throw error;
        }
    }

    /**
     * 로봇 상태 조회
     */
    async getRobotStatus() {
        return this.request('/robot/status');
    }

    /**
     * 로봇 전진 명령
     */
    async moveForward(speed = 50, distance = 100) {
        return this.request('/robot/move/forward', {
            method: 'POST',
            body: JSON.stringify({
                speed,
                distance,
                user_id: this.userId
            })
        });
    }

    /**
     * 로봇 회전 명령
     */
    async turn(direction, angle = 90, speed = 30) {
        return this.request('/robot/move/turn', {
            method: 'POST',
            body: JSON.stringify({
                direction,
                angle,
                speed,
                user_id: this.userId
            })
        });
    }

    /**
     * 로봇 정지 명령
     */
    async stop() {
        return this.request('/robot/stop', {
            method: 'POST',
            body: JSON.stringify({
                user_id: this.userId
            })
        });
    }

    /**
     * 센서 데이터 조회
     */
    async getSensorData() {
        return this.request('/sensors/distance');
    }

    /**
     * 배터리 상태 조회
     */
    async getBatteryStatus() {
        return this.request('/sensors/battery');
    }

    /**
     * 위치 데이터 조회
     */
    async getPosition() {
        return this.request('/sensors/position');
    }

    /**
     * 자연어 명령 파싱
     */
    async parseCommand(message) {
        return this.request('/nlp/parse-command', {
            method: 'POST',
            body: JSON.stringify({
                message,
                user_id: this.userId,
                session_id: this.sessionId
            })
        });
    }

    /**
     * 지원 명령어 목록 조회
     */
    async getSupportedCommands() {
        return this.request('/nlp/commands');
    }

    /**
     * 사용자 패턴 분석
     */
    async getUserPatterns(days = 7) {
        return this.request(`/analytics/user-patterns?user_id=${this.userId}&days=${days}`);
    }

    /**
     * 스마트 제안 조회
     */
    async getSmartSuggestions(context = 'idle') {
        return this.request(`/analytics/suggestions?user_id=${this.userId}&context=${context}`);
    }

    /**
     * 사용자 피드백 제출
     */
    async submitFeedback(commandId, satisfaction, feedback = '') {
        return this.request('/analytics/feedback', {
            method: 'POST',
            body: JSON.stringify({
                user_id: this.userId,
                command_id: commandId,
                satisfaction,
                feedback,
                timestamp: new Date().toISOString()
            })
        });
    }

    /**
     * LED 표정 설정
     */
    async setLEDExpression(expression, duration = 3000) {
        return this.request('/expression/led', {
            method: 'POST',
            body: JSON.stringify({
                expression,
                duration,
                user_id: this.userId
            })
        });
    }

    /**
     * 버저 소리 설정
     */
    async setBuzzerSound(sound, frequency = 1000, duration = 500) {
        return this.request('/expression/buzzer', {
            method: 'POST',
            body: JSON.stringify({
                sound,
                frequency,
                duration,
                user_id: this.userId
            })
        });
    }

    /**
     * 헬스 체크
     */
    async healthCheck() {
        try {
            console.log('healthCheck API 호출 시작...');
            const response = await fetch('http://localhost:8000/health');
            console.log('healthCheck 응답 상태:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('healthCheck 응답 데이터:', data);
            return data;
        } catch (error) {
            console.error('healthCheck API 호출 실패:', error);
            throw error;
        }
    }

    /**
     * 연결된 로봇 상태 조회
     */
    async getConnectedRobots() {
        return this.request('/robot/robots/status');
    }

    /**
     * 특정 로봇 상세 상태 조회
     */
    async getRobotDetailedStatus(robotId = 'deks_001') {
        return this.request(`/robot/robots/${robotId}/status`);
    }

    // ==================== 채팅 API ====================

    /**
     * 채팅 메시지 전송
     */
    async sendChatMessage(message, sessionId = null) {
        return this.request('/chat/message', {
            method: 'POST',
            body: JSON.stringify({
                message,
                user_id: this.userId,
                session_id: sessionId || this.sessionId
            })
        });
    }

    /**
     * 채팅 기록 조회
     */
    async getChatHistory(sessionId = null, limit = 50) {
        const params = new URLSearchParams({
            user_id: this.userId,
            limit: limit.toString()
        });
        
        if (sessionId) {
            params.append('session_id', sessionId);
        }

        return this.request(`/chat/history?${params.toString()}`);
    }

    /**
     * 채팅 컨텍스트 조회
     */
    async getChatContext(sessionId = null) {
        const params = new URLSearchParams({
            user_id: this.userId
        });
        
        if (sessionId) {
            params.append('session_id', sessionId);
        }

        return this.request(`/chat/context?${params.toString()}`);
    }

    /**
     * 채팅 컨텍스트 업데이트
     */
    async updateChatContext(context, sessionId = null) {
        return this.request('/chat/context', {
            method: 'PUT',
            body: JSON.stringify({
                user_id: this.userId,
                session_id: sessionId || this.sessionId,
                context
            })
        });
    }

    /**
     * 감정 상태 조회
     */
    async getEmotionState(sessionId = null) {
        const params = new URLSearchParams({
            user_id: this.userId
        });
        
        if (sessionId) {
            params.append('session_id', sessionId);
        }

        return this.request(`/chat/emotion?${params.toString()}`);
    }

    /**
     * 감정 상태 업데이트
     */
    async updateEmotionState(emotion, sessionId = null) {
        return this.request('/chat/emotion', {
            method: 'PUT',
            body: JSON.stringify({
                user_id: this.userId,
                session_id: sessionId || this.sessionId,
                emotion
            })
        });
    }

    /**
     * 대화 패턴 학습 데이터 제출
     */
    async submitLearningData(interactionData) {
        return this.request('/chat/learn', {
            method: 'POST',
            body: JSON.stringify({
                user_id: this.userId,
                session_id: this.sessionId,
                ...interactionData
            })
        });
    }
}

// 전역 API 인스턴스
window.deksAPI = new DeksAPI();
