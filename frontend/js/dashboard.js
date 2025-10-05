/**
 * 대시보드 메인 로직
 * UI 상호작용과 데이터 표시를 담당합니다.
 */

class DeksDashboard {
    constructor() {
        this.api = window.deksAPI;
        this.isConnected = false;
        this.updateInterval = null;
        this.commandHistory = [];
        this.sensorAutoRefresh = true;
        
        this.init();
    }

    /**
     * 대시보드 초기화
     */
    init() {
        this.setupEventListeners();
        this.checkConnection();
        this.loadInitialData();
        this.startAutoUpdate();
        
        console.log('Deks 대시보드 초기화 완료');
    }

    /**
     * 이벤트 리스너 설정
     */
    setupEventListeners() {
        // 로봇 제어 버튼들
        document.getElementById('moveForward').addEventListener('click', () => {
            this.executeCommand('move_forward');
        });

        document.getElementById('turnLeft').addEventListener('click', () => {
            this.executeCommand('turn_left');
        });

        document.getElementById('turnRight').addEventListener('click', () => {
            this.executeCommand('turn_right');
        });

        document.getElementById('stopRobot').addEventListener('click', () => {
            this.executeCommand('stop');
        });

        document.getElementById('spinRobot').addEventListener('click', () => {
            this.executeCommand('spin');
        });

        // 자연어 명령 입력
        document.getElementById('commandInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendNaturalLanguageCommand();
            }
        });

        document.getElementById('sendCommand').addEventListener('click', () => {
            this.sendNaturalLanguageCommand();
        });

        // 추천 명령어 클릭
        document.querySelectorAll('.suggestion-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const command = tag.getAttribute('data-command');
                document.getElementById('commandInput').value = command;
                this.sendNaturalLanguageCommand();
            });
        });

        // 파라미터 입력 필드 값 변경 및 검증
        document.getElementById('speedInput').addEventListener('input', (e) => {
            let value = parseInt(e.target.value);
            // 빈 값이나 NaN은 허용 (사용자가 입력 중일 수 있음)
            if (isNaN(value)) return;
            
            // 범위 초과 시 경고 메시지
            if (value < 0) {
                this.showToast('속도는 0 이상이어야 합니다.', 'error');
                e.target.value = 0;
            } else if (value > 100) {
                this.showToast('속도는 100 이하여야 합니다.', 'error');
                e.target.value = 100;
            }
        });

        document.getElementById('distanceInput').addEventListener('input', (e) => {
            let value = parseInt(e.target.value);
            // 빈 값이나 NaN은 허용 (사용자가 입력 중일 수 있음)
            if (isNaN(value)) return;
            
            // 범위 초과 시 경고 메시지
            if (value < 0) {
                this.showToast('거리는 0 이상이어야 합니다.', 'error');
                e.target.value = 0;
            } else if (value > 200) {
                this.showToast('거리는 200 이하여야 합니다.', 'error');
                e.target.value = 200;
            }
        });

        // 키보드 입력 처리 (숫자 키패드)
        document.getElementById('speedInput').addEventListener('keydown', (e) => {
            // 숫자 키패드 (0-9, Numpad0-Numpad9)
            if (e.key >= '0' && e.key <= '9' || 
                e.key === 'Numpad0' || e.key === 'Numpad1' || e.key === 'Numpad2' || 
                e.key === 'Numpad3' || e.key === 'Numpad4' || e.key === 'Numpad5' || 
                e.key === 'Numpad6' || e.key === 'Numpad7' || e.key === 'Numpad8' || 
                e.key === 'Numpad9') {
                // 숫자 입력 허용
                return;
            }
            
            // 허용되는 키들 (백스페이스, 삭제, 탭, 엔터, 화살표 키)
            if (['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
                return;
            }
            
            // 다른 키들은 차단
            e.preventDefault();
        });

        document.getElementById('distanceInput').addEventListener('keydown', (e) => {
            // 숫자 키패드 (0-9, Numpad0-Numpad9)
            if (e.key >= '0' && e.key <= '9' || 
                e.key === 'Numpad0' || e.key === 'Numpad1' || e.key === 'Numpad2' || 
                e.key === 'Numpad3' || e.key === 'Numpad4' || e.key === 'Numpad5' || 
                e.key === 'Numpad6' || e.key === 'Numpad7' || e.key === 'Numpad8' || 
                e.key === 'Numpad9') {
                // 숫자 입력 허용
                return;
            }
            
            // 허용되는 키들 (백스페이스, 삭제, 탭, 엔터, 화살표 키)
            if (['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
                return;
            }
            
            // 다른 키들은 차단
            e.preventDefault();
        });

        // 포커스 아웃 시 값 검증
        document.getElementById('speedInput').addEventListener('blur', (e) => {
            let value = parseInt(e.target.value);
            if (isNaN(value) || value < 0) {
                this.showToast('속도는 0 이상이어야 합니다.', 'error');
                e.target.value = 0;
            } else if (value > 100) {
                this.showToast('속도는 100 이하여야 합니다.', 'error');
                e.target.value = 100;
            }
        });

        document.getElementById('distanceInput').addEventListener('blur', (e) => {
            let value = parseInt(e.target.value);
            if (isNaN(value) || value < 0) {
                this.showToast('거리는 0 이상이어야 합니다.', 'error');
                e.target.value = 0;
            } else if (value > 200) {
                this.showToast('거리는 200 이하여야 합니다.', 'error');
                e.target.value = 200;
            }
        });

        // 센서 자동 새로고침 토글
        document.getElementById('sensorAutoRefresh').addEventListener('change', (e) => {
            this.sensorAutoRefresh = e.target.checked;
        });

        // 상태 새로고침 버튼
        document.getElementById('refreshStatus').addEventListener('click', () => {
            this.updateRobotStatus();
        });
    }

    /**
     * 연결 상태 확인
     */
    async checkConnection() {
        try {
            const response = await this.api.healthCheck();
            console.log('연결 상태 확인 성공:', response);
            this.setConnectionStatus(true);
        } catch (error) {
            console.error('연결 상태 확인 실패:', error);
            this.setConnectionStatus(false);
        }
    }

    /**
     * 연결 상태 표시 업데이트
     */
    setConnectionStatus(connected) {
        this.isConnected = connected;
        const statusElement = document.getElementById('connectionStatus');
        const icon = statusElement.querySelector('i');
        const text = statusElement.querySelector('span');

        if (connected) {
            statusElement.className = 'status-indicator connected';
            icon.className = 'fas fa-circle';
            text.textContent = '연결됨';
            console.log('연결 상태: 연결됨');
        } else {
            statusElement.className = 'status-indicator disconnected';
            icon.className = 'fas fa-circle';
            text.textContent = '연결 끊김';
            console.log('연결 상태: 연결 끊김');
        }
    }

    /**
     * 초기 데이터 로드
     */
    async loadInitialData() {
        await this.updateRobotStatus();
        await this.updateSensorData();
        await this.loadSmartSuggestions();
    }

    /**
     * 로봇 상태 업데이트
     */
    async updateRobotStatus() {
        try {
            const status = await this.api.getRobotStatus();
            this.displayRobotStatus(status);
        } catch (error) {
            console.error('로봇 상태 업데이트 실패:', error);
            this.showToast('로봇 상태를 불러올 수 없습니다.', 'error');
        }
    }

    /**
     * 로봇 상태 표시
     */
    displayRobotStatus(status) {
        const robotStatus = status.robot_status || status;
        
        // 위치 정보
        if (robotStatus.position) {
            document.getElementById('robotPosition').textContent = 
                `X: ${robotStatus.position.x || 0}, Y: ${robotStatus.position.y || 0}`;
        }

        // 방향 정보
        document.getElementById('robotOrientation').textContent = 
            `${robotStatus.orientation || 0}°`;

        // 배터리 정보
        const batteryLevel = robotStatus.battery || 85;
        document.getElementById('batteryLevel').style.width = `${batteryLevel}%`;
        document.getElementById('batteryText').textContent = `${batteryLevel}%`;

        // 로봇 상태
        const stateElement = document.getElementById('robotState');
        const isMoving = robotStatus.is_moving || false;
        
        if (isMoving) {
            stateElement.textContent = '이동 중';
            stateElement.className = 'status-badge moving';
        } else {
            stateElement.textContent = '대기 중';
            stateElement.className = 'status-badge waiting';
        }
    }

    /**
     * 센서 데이터 업데이트
     */
    async updateSensorData() {
        try {
            const sensorData = await this.api.getSensorData();
            this.displaySensorData(sensorData);
        } catch (error) {
            console.error('센서 데이터 업데이트 실패:', error);
        }
    }

    /**
     * 센서 데이터 표시
     */
    displaySensorData(data) {
        // 전방 적외선 센서 (장애물 감지)
        document.getElementById('frontDistance').textContent = `${data.front || 0} ${data.unit || 'cm'}`;
        
        // 낙하 감지 (적외선 센서)
        const dropElement = document.getElementById('dropDetection');
        if (data.drop_detection) {
            dropElement.textContent = '위험';
            dropElement.className = 'sensor-value danger';
        } else {
            dropElement.textContent = '안전';
            dropElement.className = 'sensor-value safe';
        }
    }

    /**
     * 스마트 제안 로드
     */
    async loadSmartSuggestions() {
        try {
            const suggestions = await this.api.getSmartSuggestions();
            this.displaySmartSuggestions(suggestions);
        } catch (error) {
            console.error('스마트 제안 로드 실패:', error);
        }
    }

    /**
     * 스마트 제안 표시
     */
    displaySmartSuggestions(suggestions) {
        const container = document.getElementById('suggestionTags');
        container.innerHTML = '';

        const suggestionList = suggestions.suggestions || suggestions;
        
        suggestionList.slice(0, 4).forEach(suggestion => {
            const tag = document.createElement('span');
            tag.className = 'suggestion-tag';
            tag.textContent = suggestion.command || suggestion;
            tag.setAttribute('data-command', suggestion.command || suggestion);
            tag.addEventListener('click', () => {
                document.getElementById('commandInput').value = suggestion.command || suggestion;
                this.sendNaturalLanguageCommand();
            });
            container.appendChild(tag);
        });
    }

    /**
     * 명령 실행
     */
    async executeCommand(action) {
        this.showLoading(true);
        
        try {
            let result;
            const speed = parseInt(document.getElementById('speedInput').value);
            const distance = parseInt(document.getElementById('distanceInput').value);

            switch (action) {
                case 'move_forward':
                    result = await this.api.moveForward(speed, distance);
                    break;
                case 'turn_left':
                    result = await this.api.turn('left', 90, speed);
                    break;
                case 'turn_right':
                    result = await this.api.turn('right', 90, speed);
                    break;
                case 'stop':
                    result = await this.api.stop();
                    break;
                case 'spin':
                    result = await this.api.turn('left', 360, speed);
                    break;
                default:
                    throw new Error('알 수 없는 명령입니다.');
            }

            this.showToast(result.message || '명령이 실행되었습니다.', 'success');
            this.addToCommandHistory(result.message || action, true);
            
            // 상태 업데이트
            setTimeout(() => {
                this.updateRobotStatus();
                this.updateSensorData();
            }, 1000);

        } catch (error) {
            console.error('명령 실행 실패:', error);
            this.showToast('명령 실행에 실패했습니다.', 'error');
            this.addToCommandHistory('명령 실행 실패', false);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 자연어 명령 전송
     */
    async sendNaturalLanguageCommand() {
        const input = document.getElementById('commandInput');
        const message = input.value.trim();

        if (!message) {
            this.showToast('명령어를 입력해주세요.', 'error');
            return;
        }

        this.showLoading(true);
        input.value = '';

        try {
            const result = await this.api.parseCommand(message);
            
            if (result.success) {
                this.showToast(result.response || '명령을 이해했습니다.', 'success');
                this.addToCommandHistory(message, true);
                
                // 파싱된 명령이 있으면 실행
                if (result.action) {
                    await this.executeParsedCommand(result);
                }
            } else {
                this.showToast(result.message || '명령을 이해할 수 없습니다.', 'error');
                this.addToCommandHistory(message, false);
                
                // 제안 표시
                if (result.suggestions) {
                    this.showSuggestions(result.suggestions);
                }
            }

        } catch (error) {
            console.error('자연어 명령 처리 실패:', error);
            this.showToast('명령 처리에 실패했습니다.', 'error');
            this.addToCommandHistory(message, false);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 파싱된 명령 실행
     */
    async executeParsedCommand(result) {
        // 실제 로봇 제어는 백엔드에서 처리되므로 여기서는 상태 업데이트만
        setTimeout(() => {
            this.updateRobotStatus();
            this.updateSensorData();
        }, 1000);
    }

    /**
     * 명령어 히스토리에 추가
     */
    addToCommandHistory(command, success) {
        const historyItem = {
            command,
            success,
            timestamp: new Date().toLocaleTimeString()
        };

        this.commandHistory.unshift(historyItem);
        
        // 최대 10개까지만 보관
        if (this.commandHistory.length > 10) {
            this.commandHistory = this.commandHistory.slice(0, 10);
        }

        this.displayCommandHistory();
    }

    /**
     * 명령어 히스토리 표시
     */
    displayCommandHistory() {
        const container = document.getElementById('commandHistory');
        container.innerHTML = '';

        this.commandHistory.slice(0, 5).forEach(item => {
            const historyElement = document.createElement('div');
            historyElement.className = `history-item ${item.success ? 'success' : 'error'}`;
            historyElement.innerHTML = `
                <span>${item.command}</span>
                <span class="history-time">${item.timestamp}</span>
            `;
            container.appendChild(historyElement);
        });
    }

    /**
     * 제안 표시
     */
    showSuggestions(suggestions) {
        // TODO: 제안을 더 자세히 표시하는 UI 구현
        console.log('제안:', suggestions);
    }

    /**
     * 자동 업데이트 시작
     */
    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            if (this.isConnected) {
                this.updateRobotStatus();
                
                if (this.sensorAutoRefresh) {
                    this.updateSensorData();
                }
            }
        }, 5000); // 5초마다 업데이트

        // 10초마다 연결 상태 확인
        this.connectionCheckInterval = setInterval(() => {
            this.checkConnection();
        }, 10000);
    }

    /**
     * 자동 업데이트 중지
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * 로딩 표시
     */
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    /**
     * 토스트 알림 표시
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 'info-circle';
        
        toast.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// 페이지 로드 시 대시보드 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.deksDashboard = new DeksDashboard();
});
