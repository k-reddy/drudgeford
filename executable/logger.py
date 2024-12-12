import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class GameLog:
    game_id: str
    start_time: datetime
    port: int
    errors: List[tuple[datetime, str]] = field(default_factory=list)
    end_time: Optional[datetime] = None
    end_status: Optional[str] = None
    end_error: Optional[str] = None


class GameLogger:
    def __init__(self, log_dir: str = "logs"):
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Store active game logs
        self.active_games: Dict[str, GameLog] = {}

        # Setup game lifecycle logger
        self.game_logger = logging.getLogger("game_lifecycle")
        game_handler = logging.FileHandler(os.path.join(log_dir, "game_lifecycle.log"))
        game_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.game_logger.addHandler(game_handler)
        self.game_logger.setLevel(logging.INFO)

        # Setup rate limit logger
        self.rate_logger = logging.getLogger("rate_limit")
        rate_handler = logging.FileHandler(os.path.join(log_dir, "rate_limit.log"))
        rate_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.rate_logger.addHandler(rate_handler)
        self.rate_logger.setLevel(logging.WARNING)

        # Setup port allocation logger
        self.port_logger = logging.getLogger("port_allocation")
        port_handler = logging.FileHandler(os.path.join(log_dir, "port_allocation.log"))
        port_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.port_logger.addHandler(port_handler)
        self.port_logger.setLevel(logging.INFO)

        # Setup general error logger
        self.error_logger = logging.getLogger("general_error")
        error_handler = logging.FileHandler(os.path.join(log_dir, "general_error.log"))
        error_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.error_logger.addHandler(error_handler)
        self.error_logger.setLevel(logging.ERROR)

    def log_game_start(self, game_id: str, port: int) -> None:
        """Log the start of a new game"""
        now = datetime.now()
        game_log = GameLog(game_id=game_id, start_time=now, port=port)
        self.active_games[game_id] = game_log
        self.game_logger.info(f"GameID: {game_id}\n- Started: {now} on port {port}")

    def log_game_error(self, game_id: str, error: str) -> None:
        """Log an error for a specific game"""
        now = datetime.now()
        if game_id in self.active_games:
            self.active_games[game_id].errors.append((now, error))
            self.game_logger.error(f'GameID: {game_id}\n- Error: {now} "{error}"')
        else:
            # If we can't find the game, log it as a general error
            self.error_logger.error(f"Error for unknown game {game_id}: {error}")

    def log_game_end(
        self, game_id: str, status: str, error: Optional[str] = None
    ) -> None:
        """Log the end of a game"""
        now = datetime.now()
        if game_id in self.active_games:
            game = self.active_games[game_id]
            game.end_time = now
            game.end_status = status
            game.end_error = error

            msg = f"GameID: {game_id}\n- Ended: {now} with status: {status}"
            if error:
                msg += f' "{error}"'
            self.game_logger.info(msg)

            # Write complete game log
            self._write_complete_game_log(game)
            # Remove from active games
            del self.active_games[game_id]

    def log_rate_limit(self, ip: str) -> None:
        """Log a rate limit event"""
        self.rate_logger.warning(f"IP {ip} hit daily limit (20 games/24hrs)")

    def log_port_allocation(
        self, port: Optional[int], total_ports: int, used_ports: int
    ) -> None:
        """Log port allocation status"""
        if port is None:
            self.port_logger.warning(
                f"Failed to allocate port - all ports in range 5000-{5000+total_ports-1} in use"
            )
        else:
            action = "allocated" if port else "freed"
            self.port_logger.info(
                f"Port {port} {action} - {used_ports}/{total_ports} ports in use"
            )

    def log_general_error(self, error: str) -> None:
        """Log a general server error"""
        self.error_logger.error(f'Server error: "{error}"')

    def _write_complete_game_log(self, game: GameLog) -> None:
        """Write a complete game log entry when game ends"""
        log_entry = [
            f"GameID: {game.game_id}",
            f"- Started: {game.start_time} on port {game.port}",
        ]

        # Add any errors that occurred during the game
        for error_time, error_msg in game.errors:
            log_entry.append(f'- Error: {error_time} "{error_msg}"')

        # Add end status
        log_entry.append(f"- Ended: {game.end_time} with status: {game.end_status}")
        if game.end_error:
            log_entry.append(f'  Error: "{game.end_error}"')

        self.game_logger.info("\n".join(log_entry))
