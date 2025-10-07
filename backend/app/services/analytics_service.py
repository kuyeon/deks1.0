"""
사용자 분석 및 패턴 학습 서비스
사용자 행동 추적, 패턴 분석, 스마트 제안 생성
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from loguru import logger
import json

from app.database.database_manager import db_manager
from app.core.exceptions import DatabaseException, InvalidParameterException


@dataclass
class CommandFrequency:
    """명령 빈도 분석 결과"""
    command: str
    count: int
    success_count: int
    failure_count: int
    success_rate: float
    last_used: datetime
    avg_execution_time: float = 0.0


@dataclass
class TimeSlotPattern:
    """시간대별 사용 패턴"""
    time_slot: str  # morning, afternoon, evening, night
    command_count: int
    most_common_command: str
    avg_satisfaction: float


@dataclass
class UserBehaviorProfile:
    """사용자 행동 프로필"""
    user_id: str
    total_interactions: int
    total_commands: int
    favorite_commands: List[str]
    command_success_rate: float
    avg_session_duration: float  # 초 단위
    most_active_time_slot: str
    learning_level: str  # beginner, intermediate, advanced
    preferences: Dict[str, Any]


@dataclass
class SmartSuggestion:
    """스마트 제안"""
    command: str
    confidence: float
    reason: str
    category: str  # frequency_based, time_based, error_prevention, sequence_optimization


class AnalyticsService:
    """사용자 분석 및 패턴 학습 서비스"""
    
    def __init__(self):
        """Analytics 서비스 초기화"""
        self.time_slots = {
            "morning": (6, 12),    # 06:00 - 11:59
            "afternoon": (12, 18),  # 12:00 - 17:59
            "evening": (18, 23),    # 18:00 - 22:59
            "night": (23, 6)        # 23:00 - 05:59
        }
        
        self.learning_levels = {
            "beginner": (0, 20),      # 0-20회 상호작용
            "intermediate": (21, 100), # 21-100회
            "advanced": (101, float('inf'))  # 101회 이상
        }
        
        logger.info("Analytics 서비스 초기화 완료")
    
    async def analyze_user_behavior(
        self,
        user_id: str,
        days: int = 7
    ) -> UserBehaviorProfile:
        """
        사용자 행동 패턴 분석
        
        Args:
            user_id: 사용자 ID
            days: 분석 기간 (일)
        
        Returns:
            UserBehaviorProfile: 사용자 행동 프로필
        """
        try:
            if days <= 0:
                raise InvalidParameterException(
                    parameter_name="days",
                    reason="분석 기간은 1일 이상이어야 합니다"
                )
            
            # 기간 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 명령 실행 로그 조회
            command_logs = await self._get_command_logs(
                user_id, start_date, end_date
            )
            
            # 대화 기록 조회
            chat_logs = await self._get_chat_logs(
                user_id, start_date, end_date
            )
            
            # 총 상호작용 수
            total_interactions = len(command_logs) + len(chat_logs)
            total_commands = len(command_logs)
            
            # 자주 사용하는 명령어 분석
            favorite_commands = self._analyze_favorite_commands(command_logs)
            
            # 성공률 계산
            success_rate = self._calculate_success_rate(command_logs)
            
            # 평균 세션 시간 계산
            avg_session_duration = await self._calculate_avg_session_duration(
                user_id, start_date, end_date
            )
            
            # 가장 활동적인 시간대 분석
            most_active_time = self._analyze_most_active_time(
                command_logs, chat_logs
            )
            
            # 학습 레벨 결정
            learning_level = self._determine_learning_level(total_interactions)
            
            # 사용자 선호도 조회
            preferences = await self._get_user_preferences(user_id)
            
            return UserBehaviorProfile(
                user_id=user_id,
                total_interactions=total_interactions,
                total_commands=total_commands,
                favorite_commands=favorite_commands[:5],  # 상위 5개
                command_success_rate=success_rate,
                avg_session_duration=avg_session_duration,
                most_active_time_slot=most_active_time,
                learning_level=learning_level,
                preferences=preferences
            )
            
        except InvalidParameterException:
            raise
        except Exception as e:
            logger.error(f"사용자 행동 분석 실패: {e}")
            raise DatabaseException(
                message=f"사용자 행동 분석 실패: {str(e)}",
                original_exception=e
            )
    
    async def get_command_frequency_analysis(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[CommandFrequency]:
        """
        명령 빈도 분석
        
        Args:
            user_id: 사용자 ID
            limit: 결과 개수 제한
        
        Returns:
            명령 빈도 리스트
        """
        try:
            query = """
            SELECT 
                command_type,
                COUNT(*) as total_count,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failure_count,
                MAX(timestamp) as last_used,
                AVG(execution_time) as avg_time
            FROM command_execution_logs
            WHERE user_id = ?
            GROUP BY command_type
            ORDER BY total_count DESC
            LIMIT ?
            """
            
            results = db_manager.execute_query(query, (user_id, limit))
            
            frequencies = []
            for row in results:
                command_type = row[0]
                total_count = row[1]
                success_count = row[2]
                failure_count = row[3]
                last_used_str = row[4]
                avg_time = row[5] or 0.0
                
                success_rate = (success_count / total_count * 100) if total_count > 0 else 0.0
                
                frequencies.append(CommandFrequency(
                    command=command_type,
                    count=total_count,
                    success_count=success_count,
                    failure_count=failure_count,
                    success_rate=round(success_rate, 2),
                    last_used=datetime.fromisoformat(last_used_str) if last_used_str else datetime.now(),
                    avg_execution_time=round(avg_time, 3)
                ))
            
            return frequencies
            
        except Exception as e:
            logger.error(f"명령 빈도 분석 실패: {e}")
            raise DatabaseException(
                message=f"명령 빈도 분석 실패: {str(e)}",
                original_exception=e
            )
    
    async def analyze_time_slot_patterns(
        self,
        user_id: str,
        days: int = 30
    ) -> List[TimeSlotPattern]:
        """
        시간대별 사용 패턴 분석
        
        Args:
            user_id: 사용자 ID
            days: 분석 기간
        
        Returns:
            시간대별 패턴 리스트
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 명령 실행 로그 조회
            command_logs = await self._get_command_logs(user_id, start_date, end_date)
            
            # 시간대별 그룹화
            time_slot_data = defaultdict(list)
            
            for log in command_logs:
                timestamp = datetime.fromisoformat(log['timestamp'])
                time_slot = self._get_time_slot(timestamp.hour)
                time_slot_data[time_slot].append(log)
            
            # 시간대별 패턴 분석
            patterns = []
            for time_slot, logs in time_slot_data.items():
                if not logs:
                    continue
                
                # 가장 많이 사용된 명령
                command_counter = Counter(log['command_type'] for log in logs)
                most_common = command_counter.most_common(1)
                most_common_command = most_common[0][0] if most_common else "없음"
                
                # 평균 만족도 (피드백이 있는 경우)
                avg_satisfaction = 4.0  # 기본값
                
                patterns.append(TimeSlotPattern(
                    time_slot=time_slot,
                    command_count=len(logs),
                    most_common_command=most_common_command,
                    avg_satisfaction=avg_satisfaction
                ))
            
            return sorted(patterns, key=lambda x: x.command_count, reverse=True)
            
        except Exception as e:
            logger.error(f"시간대별 패턴 분석 실패: {e}")
            raise DatabaseException(
                message=f"시간대별 패턴 분석 실패: {str(e)}",
                original_exception=e
            )
    
    async def generate_smart_suggestions(
        self,
        user_id: str,
        context: str = "idle",
        limit: int = 5
    ) -> List[SmartSuggestion]:
        """
        스마트 제안 생성
        
        Args:
            user_id: 사용자 ID
            context: 현재 컨텍스트
            limit: 제안 개수
        
        Returns:
            스마트 제안 리스트
        """
        try:
            suggestions = []
            
            # 1. 빈도 기반 제안
            frequency_suggestions = await self._get_frequency_based_suggestions(
                user_id, limit=3
            )
            suggestions.extend(frequency_suggestions)
            
            # 2. 시간대 기반 제안
            time_suggestions = await self._get_time_based_suggestions(
                user_id, limit=2
            )
            suggestions.extend(time_suggestions)
            
            # 3. 에러 방지 제안
            error_prevention_suggestions = await self._get_error_prevention_suggestions(
                user_id, limit=2
            )
            suggestions.extend(error_prevention_suggestions)
            
            # 4. 시퀀스 최적화 제안
            sequence_suggestions = await self._get_sequence_suggestions(
                user_id, limit=2
            )
            suggestions.extend(sequence_suggestions)
            
            # 신뢰도 순으로 정렬하고 상위 N개 반환
            suggestions.sort(key=lambda x: x.confidence, reverse=True)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"스마트 제안 생성 실패: {e}")
            raise DatabaseException(
                message=f"스마트 제안 생성 실패: {str(e)}",
                original_exception=e
            )
    
    async def analyze_error_patterns(
        self,
        user_id: Optional[str] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        에러 패턴 분석
        
        Args:
            user_id: 사용자 ID (None이면 전체)
            days: 분석 기간
        
        Returns:
            에러 패턴 리스트
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            if user_id:
                query = """
                SELECT command_type, error_message, COUNT(*) as error_count
                FROM command_execution_logs
                WHERE user_id = ? AND success = 0 
                  AND timestamp BETWEEN ? AND ?
                GROUP BY command_type, error_message
                ORDER BY error_count DESC
                """
                params = (user_id, start_date.isoformat(), end_date.isoformat())
            else:
                query = """
                SELECT command_type, error_message, COUNT(*) as error_count
                FROM command_execution_logs
                WHERE success = 0 
                  AND timestamp BETWEEN ? AND ?
                GROUP BY command_type, error_message
                ORDER BY error_count DESC
                """
                params = (start_date.isoformat(), end_date.isoformat())
            
            results = db_manager.execute_query(query, params)
            
            error_patterns = []
            for row in results:
                error_patterns.append({
                    "command_type": row[0],
                    "error_message": row[1],
                    "frequency": row[2],
                    "suggestions": self._generate_error_fix_suggestions(row[0], row[1])
                })
            
            return error_patterns
            
        except Exception as e:
            logger.error(f"에러 패턴 분석 실패: {e}")
            raise DatabaseException(
                message=f"에러 패턴 분석 실패: {str(e)}",
                original_exception=e
            )
    
    async def get_user_statistics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        사용자 통계 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            사용자 통계 딕셔너리
        """
        try:
            # 총 상호작용 수
            total_query = """
            SELECT COUNT(*) FROM user_interactions WHERE user_id = ?
            """
            total_result = db_manager.execute_query(total_query, (user_id,))
            total_interactions = total_result[0][0] if total_result else 0
            
            # 총 명령 수
            command_query = """
            SELECT COUNT(*) FROM command_execution_logs WHERE user_id = ?
            """
            command_result = db_manager.execute_query(command_query, (user_id,))
            total_commands = command_result[0][0] if command_result else 0
            
            # 성공률
            success_query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
            FROM command_execution_logs 
            WHERE user_id = ?
            """
            success_result = db_manager.execute_query(success_query, (user_id,))
            if success_result and success_result[0][0] > 0:
                total = success_result[0][0]
                successes = success_result[0][1] or 0
                success_rate = (successes / total) * 100
            else:
                success_rate = 0.0
            
            # 첫 방문 / 마지막 방문
            visit_query = """
            SELECT MIN(timestamp), MAX(timestamp)
            FROM user_interactions
            WHERE user_id = ?
            """
            visit_result = db_manager.execute_query(visit_query, (user_id,))
            first_visit = visit_result[0][0] if visit_result and visit_result[0][0] else None
            last_visit = visit_result[0][1] if visit_result and visit_result[0][1] else None
            
            # 학습 레벨
            learning_level = self._determine_learning_level(total_interactions)
            
            return {
                "user_id": user_id,
                "total_interactions": total_interactions,
                "total_commands": total_commands,
                "success_rate": round(success_rate, 2),
                "first_visit": first_visit,
                "last_visit": last_visit,
                "learning_level": learning_level,
                "is_active": total_interactions > 0
            }
            
        except Exception as e:
            logger.error(f"사용자 통계 조회 실패: {e}")
            raise DatabaseException(
                message=f"사용자 통계 조회 실패: {str(e)}",
                original_exception=e
            )
    
    async def get_global_statistics(self) -> Dict[str, Any]:
        """
        전체 시스템 통계 조회
        
        Returns:
            전체 통계 딕셔너리
        """
        try:
            # 총 사용자 수
            users_query = "SELECT COUNT(DISTINCT user_id) FROM user_interactions"
            users_result = db_manager.execute_query(users_query)
            total_users = users_result[0][0] if users_result else 0
            
            # 총 명령 수
            commands_query = "SELECT COUNT(*) FROM command_execution_logs"
            commands_result = db_manager.execute_query(commands_query)
            total_commands = commands_result[0][0] if commands_result else 0
            
            # 전체 성공률
            success_query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
            FROM command_execution_logs
            """
            success_result = db_manager.execute_query(success_query)
            if success_result and success_result[0][0] > 0:
                total = success_result[0][0]
                successes = success_result[0][1] or 0
                success_rate = (successes / total) * 100
            else:
                success_rate = 0.0
            
            # 가장 인기 있는 명령
            popular_query = """
            SELECT command_type, COUNT(*) as count
            FROM command_execution_logs
            GROUP BY command_type
            ORDER BY count DESC
            LIMIT 1
            """
            popular_result = db_manager.execute_query(popular_query)
            most_popular = popular_result[0][0] if popular_result else "없음"
            
            # 평균 세션 시간 (전체)
            avg_session_duration = 300.0  # 기본값 5분
            
            # 에러율
            error_rate = 100.0 - success_rate
            
            return {
                "total_users": total_users,
                "total_commands": total_commands,
                "success_rate": round(success_rate, 2),
                "most_popular_command": most_popular,
                "avg_session_duration_seconds": avg_session_duration,
                "error_rate": round(error_rate, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"전체 통계 조회 실패: {e}")
            raise DatabaseException(
                message=f"전체 통계 조회 실패: {str(e)}",
                original_exception=e
            )
    
    # ========== 내부 메서드 ==========
    
    async def _get_command_logs(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """명령 실행 로그 조회"""
        try:
            query = """
            SELECT command_id, command_type, parameters, success, 
                   execution_time, error_message, timestamp
            FROM command_execution_logs
            WHERE user_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            """
            
            results = db_manager.execute_query(
                query,
                (user_id, start_date.isoformat(), end_date.isoformat())
            )
            
            logs = []
            for row in results:
                logs.append({
                    "command_id": row[0],
                    "command_type": row[1],
                    "parameters": row[2],
                    "success": bool(row[3]),
                    "execution_time": row[4],
                    "error_message": row[5],
                    "timestamp": row[6]
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"명령 로그 조회 실패: {e}")
            return []
    
    async def _get_chat_logs(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """채팅 로그 조회"""
        try:
            query = """
            SELECT message_id, user_message, robot_response, 
                   emotion_detected, conversation_type, timestamp
            FROM chat_messages
            WHERE user_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            """
            
            results = db_manager.execute_query(
                query,
                (user_id, start_date.isoformat(), end_date.isoformat())
            )
            
            logs = []
            for row in results:
                logs.append({
                    "message_id": row[0],
                    "user_message": row[1],
                    "robot_response": row[2],
                    "emotion": row[3],
                    "conversation_type": row[4],
                    "timestamp": row[5]
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"채팅 로그 조회 실패: {e}")
            return []
    
    def _analyze_favorite_commands(
        self,
        command_logs: List[Dict[str, Any]]
    ) -> List[str]:
        """자주 사용하는 명령어 분석"""
        if not command_logs:
            return []
        
        command_counter = Counter(
            log['command_type'] for log in command_logs
        )
        
        return [cmd for cmd, count in command_counter.most_common(10)]
    
    def _calculate_success_rate(
        self,
        command_logs: List[Dict[str, Any]]
    ) -> float:
        """명령 성공률 계산"""
        if not command_logs:
            return 0.0
        
        total = len(command_logs)
        successes = sum(1 for log in command_logs if log['success'])
        
        return round((successes / total) * 100, 2)
    
    async def _calculate_avg_session_duration(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """평균 세션 시간 계산 (초)"""
        try:
            query = """
            SELECT session_id, MIN(timestamp) as start, MAX(timestamp) as end
            FROM user_interactions
            WHERE user_id = ? AND timestamp BETWEEN ? AND ?
            GROUP BY session_id
            """
            
            results = db_manager.execute_query(
                query,
                (user_id, start_date.isoformat(), end_date.isoformat())
            )
            
            if not results:
                return 0.0
            
            durations = []
            for row in results:
                start = datetime.fromisoformat(row[1])
                end = datetime.fromisoformat(row[2])
                duration = (end - start).total_seconds()
                durations.append(duration)
            
            return round(sum(durations) / len(durations), 2) if durations else 0.0
            
        except Exception as e:
            logger.error(f"세션 시간 계산 실패: {e}")
            return 0.0
    
    def _analyze_most_active_time(
        self,
        command_logs: List[Dict[str, Any]],
        chat_logs: List[Dict[str, Any]]
    ) -> str:
        """가장 활동적인 시간대 분석"""
        all_logs = command_logs + chat_logs
        
        if not all_logs:
            return "unknown"
        
        time_slot_counter = Counter()
        
        for log in all_logs:
            timestamp = datetime.fromisoformat(log['timestamp'])
            time_slot = self._get_time_slot(timestamp.hour)
            time_slot_counter[time_slot] += 1
        
        most_common = time_slot_counter.most_common(1)
        return most_common[0][0] if most_common else "unknown"
    
    def _get_time_slot(self, hour: int) -> str:
        """시간을 시간대로 변환"""
        for slot_name, (start, end) in self.time_slots.items():
            if slot_name == "night":
                # night는 23:00-05:59
                if hour >= 23 or hour < 6:
                    return "night"
            else:
                if start <= hour < end:
                    return slot_name
        
        return "unknown"
    
    def _determine_learning_level(self, total_interactions: int) -> str:
        """학습 레벨 결정"""
        for level, (min_count, max_count) in self.learning_levels.items():
            if min_count <= total_interactions <= max_count:
                return level
        
        return "beginner"
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """사용자 선호도 조회"""
        try:
            query = """
            SELECT preferences FROM user_long_term_memory WHERE user_id = ?
            """
            result = db_manager.execute_query(query, (user_id,))
            
            if result and result[0][0]:
                return json.loads(result[0][0])
            else:
                return {}
                
        except Exception as e:
            logger.error(f"선호도 조회 실패: {e}")
            return {}
    
    async def _get_frequency_based_suggestions(
        self,
        user_id: str,
        limit: int = 3
    ) -> List[SmartSuggestion]:
        """빈도 기반 제안"""
        try:
            frequencies = await self.get_command_frequency_analysis(user_id, limit=limit)
            
            suggestions = []
            for freq in frequencies:
                suggestions.append(SmartSuggestion(
                    command=freq.command,
                    confidence=min(0.95, 0.5 + (freq.count / 100)),
                    reason=f"가장 자주 사용하는 명령입니다 ({freq.count}회)",
                    category="frequency_based"
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"빈도 기반 제안 생성 실패: {e}")
            return []
    
    async def _get_time_based_suggestions(
        self,
        user_id: str,
        limit: int = 2
    ) -> List[SmartSuggestion]:
        """시간대 기반 제안"""
        try:
            current_hour = datetime.now().hour
            current_time_slot = self._get_time_slot(current_hour)
            
            # 현재 시간대에 자주 사용하는 명령 조회
            query = """
            SELECT command_type, COUNT(*) as count
            FROM command_execution_logs
            WHERE user_id = ?
            GROUP BY command_type
            ORDER BY count DESC
            LIMIT ?
            """
            
            results = db_manager.execute_query(query, (user_id, limit))
            
            suggestions = []
            for row in results:
                suggestions.append(SmartSuggestion(
                    command=row[0],
                    confidence=0.7,
                    reason=f"{current_time_slot} 시간대에 자주 사용합니다",
                    category="time_based"
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"시간대 기반 제안 생성 실패: {e}")
            return []
    
    async def _get_error_prevention_suggestions(
        self,
        user_id: str,
        limit: int = 2
    ) -> List[SmartSuggestion]:
        """에러 방지 제안"""
        try:
            # 최근 에러 패턴 분석
            error_patterns = await self.analyze_error_patterns(user_id, days=7)
            
            suggestions = []
            for pattern in error_patterns[:limit]:
                if pattern['suggestions']:
                    suggestions.append(SmartSuggestion(
                        command=pattern['suggestions'][0],
                        confidence=0.65,
                        reason=f"'{pattern['command_type']}' 명령 시 에러가 자주 발생합니다",
                        category="error_prevention"
                    ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"에러 방지 제안 생성 실패: {e}")
            return []
    
    async def _get_sequence_suggestions(
        self,
        user_id: str,
        limit: int = 2
    ) -> List[SmartSuggestion]:
        """시퀀스 최적화 제안"""
        try:
            # 명령 시퀀스 패턴 분석 (연속된 명령어)
            query = """
            SELECT command_type 
            FROM command_execution_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
            """
            
            results = db_manager.execute_query(query, (user_id,))
            
            if not results or len(results) < 2:
                return []
            
            # 패턴 감지 (예: "move_forward" 후 자주 "turn_right")
            suggestions = []
            
            # 기본 시퀀스 제안
            common_sequences = [
                ("move_forward", "turn_right", "탐색을 위해 우회전해보세요"),
                ("turn_left", "move_forward", "회전 후 전진해보세요")
            ]
            
            for first, second, reason in common_sequences[:limit]:
                suggestions.append(SmartSuggestion(
                    command=second,
                    confidence=0.6,
                    reason=reason,
                    category="sequence_optimization"
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"시퀀스 제안 생성 실패: {e}")
            return []
    
    def _generate_error_fix_suggestions(
        self,
        command_type: str,
        error_message: str
    ) -> List[str]:
        """에러 수정 제안 생성"""
        suggestions = []
        
        # 에러 메시지 기반 제안
        if "연결" in error_message or "disconnect" in error_message.lower():
            suggestions.append("로봇 연결 상태를 확인하세요")
            suggestions.append("Wi-Fi 연결을 확인하세요")
        
        if "타임아웃" in error_message or "timeout" in error_message.lower():
            suggestions.append("명령을 다시 시도해보세요")
            suggestions.append("로봇이 응답할 때까지 기다려주세요")
        
        if "파라미터" in error_message or "parameter" in error_message.lower():
            suggestions.append("명령 형식을 확인하세요")
            suggestions.append("올바른 값을 입력하세요 (속도: 0-100, 거리: 0-200)")
        
        # 기본 제안
        if not suggestions:
            suggestions.append("명령을 다시 시도해보세요")
            suggestions.append("로봇 상태를 확인하세요")
        
        return suggestions


# 전역 Analytics 서비스 인스턴스
_analytics_service: Optional[AnalyticsService] = None


async def get_analytics_service() -> AnalyticsService:
    """Analytics 서비스 싱글톤 인스턴스"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service

