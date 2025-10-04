/**
 * WebSocket 통신 모듈
 * 실시간 데이터 수신을 담당합니다.
 */

class DeksWebSocket {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        this.isConnected = false;
        
        this.init();
    }

    /**
     * WebSocket 초기화
     */
    init() {
        this.connect();
    }

    /**
     * WebSocket 연결
     */
    connect() {
        try {
            this.ws = new WebSocket('ws://localhost:8000/ws');
            
            this.ws.onopen = () => {
                console.log('WebSocket 연결됨');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.onConnectionChange(true);
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
            };

            this.ws.onclose = () => {
                console.log('WebSocket 연결 끊김');
                this.isConnected = false;
                this.onConnectionChange(false);
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket 오류:', error);
                this.isConnected = false;
                this.onConnectionChange(false);
            };

        } catch (error) {
            console.error('WebSocket 연결 실패:', error);
            this.attemptReconnect();
        }
    }

    /**
     * 메시지 처리
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            switch (message.type) {
                case 'robot_status':
                    this.handleRobotStatus(message.data);
                    break;
                case 'sensor_data':
                    this.handleSensorData(message.data);
                    break;
                case 'command_progress':
                    this.handleCommandProgress(message.data);
                    break;
                case 'error':
                    this.handleError(message.data);
                    break;
                case 'notification':
                    this.handleNotification(message.data);
                    break;
                default:
                    console.log('알 수 없는 메시지 타입:', message.type);
            }
        } catch (error) {
            console.error('메시지 파싱 오류:', error);
        }
    }

    /**
     * 로봇 상태 업데이트 처리
     */
    handleRobotStatus(data) {
        if (window.deksDashboard) {
            window.deksDashboard.displayRobotStatus(data);
        }
    }

    /**
     * 센서 데이터 업데이트 처리
     */
    handleSensorData(data) {
        if (window.deksDashboard) {
            window.deksDashboard.displaySensorData(data);
        }
    }

    /**
     * 명령 진행상황 처리
     */
    handleCommandProgress(data) {
        if (window.deksDashboard) {
            const message = `명령 진행중: ${data.progress || 0}%`;
            window.deksDashboard.showToast(message, 'info');
        }
    }

    /**
     * 오류 처리
     */
    handleError(data) {
        if (window.deksDashboard) {
            window.deksDashboard.showToast(`오류: ${data.message}`, 'error');
        }
    }

    /**
     * 알림 처리
     */
    handleNotification(data) {
        if (window.deksDashboard) {
            window.deksDashboard.showToast(data.message, 'info');
        }
    }

    /**
     * 연결 상태 변경 처리
     */
    onConnectionChange(connected) {
        if (window.deksDashboard) {
            window.deksDashboard.setConnectionStatus(connected);
        }
    }

    /**
     * 재연결 시도
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('최대 재연결 시도 횟수 초과');
            if (window.deksDashboard) {
                window.deksDashboard.showToast('서버 연결에 실패했습니다. 페이지를 새로고침해주세요.', 'error');
            }
        }
    }

    /**
     * 메시지 전송
     */
    send(message) {
        if (this.isConnected && this.ws) {
            try {
                this.ws.send(JSON.stringify(message));
                return true;
            } catch (error) {
                console.error('메시지 전송 실패:', error);
                return false;
            }
        } else {
            console.warn('WebSocket이 연결되지 않았습니다.');
            return false;
        }
    }

    /**
     * 연결 종료
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }

    /**
     * 연결 상태 확인
     */
    getConnectionState() {
        return {
            connected: this.isConnected,
            readyState: this.ws ? this.ws.readyState : WebSocket.CLOSED
        };
    }
}

// 전역 WebSocket 인스턴스
window.deksWebSocket = new DeksWebSocket();
