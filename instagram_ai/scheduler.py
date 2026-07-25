"""
Task scheduling for Instagram automation
Handles scheduled posting and comment checks
"""
import schedule
import time
from typing import Callable, Optional
from datetime import datetime
from instagram_ai.logger import Logger
from instagram_ai import config

class TaskScheduler:
    """Schedule and manage automation tasks"""
    
    def __init__(self):
        """Initialize task scheduler"""
        self.logger = Logger.get_logger(__name__)
        self.scheduler = schedule.Scheduler()
    
    def schedule_daily_post(
        self,
        task_func: Callable,
        time_str: str = "09:00",
        task_name: str = "daily_post"
    ) -> schedule.Job:
        """
        Schedule a daily posting task
        
        Args:
            task_func: Function to execute
            time_str: Time to run in HH:MM format (default: 09:00)
            task_name: Name for logging
        
        Returns:
            Scheduled job
        """
        try:
            job = self.scheduler.at(time_str).do(task_func)
            job.tag(task_name)
            self.logger.info(f"Scheduled daily task '{task_name}' at {time_str}")
            return job
        except Exception as e:
            self.logger.error(f"Failed to schedule daily task", e)
            raise
    
    def schedule_hourly_comments(
        self,
        task_func: Callable,
        task_name: str = "check_comments"
    ) -> schedule.Job:
        """
        Schedule hourly comment checking
        
        Args:
            task_func: Function to execute
            task_name: Name for logging
        
        Returns:
            Scheduled job
        """
        try:
            job = self.scheduler.every().hour.do(task_func)
            job.tag(task_name)
            self.logger.info(f"Scheduled hourly task '{task_name}'")
            return job
        except Exception as e:
            self.logger.error(f"Failed to schedule hourly task", e)
            raise
    
    def schedule_every_interval(
        self,
        task_func: Callable,
        interval: int,
        unit: str = "minutes",
        task_name: str = "interval_task"
    ) -> schedule.Job:
        """
        Schedule task at regular intervals
        
        Args:
            task_func: Function to execute
            interval: Interval count
            unit: Time unit (minutes, hours, days)
            task_name: Name for logging
        
        Returns:
            Scheduled job
        """
        try:
            if unit == "minutes":
                job = self.scheduler.every(interval).minutes.do(task_func)
            elif unit == "hours":
                job = self.scheduler.every(interval).hours.do(task_func)
            elif unit == "days":
                job = self.scheduler.every(interval).days.do(task_func)
            else:
                raise ValueError(f"Invalid time unit: {unit}")
            
            job.tag(task_name)
            self.logger.info(f"Scheduled task '{task_name}' every {interval} {unit}")
            return job
        except Exception as e:
            self.logger.error(f"Failed to schedule interval task", e)
            raise
    
    def remove_job(self, tag: str) -> bool:
        """
        Remove scheduled job by tag
        
        Args:
            tag: Job tag
        
        Returns:
            True if removed, False otherwise
        """
        try:
            self.scheduler.remove(tag)
            self.logger.info(f"Removed scheduled job: {tag}")
            return True
        except schedule.ScheduleValueError:
            self.logger.warning(f"Job not found: {tag}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove job", e)
            return False
    
    def get_jobs(self) -> list:
        """
        Get all scheduled jobs
        
        Returns:
            List of scheduled jobs
        """
        return self.scheduler.get_jobs()
    
    def clear_all_jobs(self):
        """Clear all scheduled jobs"""
        try:
            self.scheduler.clear()
            self.logger.info("Cleared all scheduled jobs")
        except Exception as e:
            self.logger.error("Failed to clear jobs", e)
    
    def run_pending(self) -> int:
        """
        Run all pending scheduled tasks
        
        Returns:
            Number of tasks run
        """
        try:
            self.logger.debug("Running pending tasks")
            return self.scheduler.run_pending()
        except Exception as e:
            self.logger.error("Error running pending tasks", e)
            return 0
    
    def run_all(self, delay_seconds: int = 0):
        """
        Run all scheduled tasks immediately
        
        Args:
            delay_seconds: Delay between tasks
        """
        try:
            self.logger.info("Running all scheduled tasks")
            self.scheduler.run_all(delay_seconds=delay_seconds)
        except Exception as e:
            self.logger.error("Error running all tasks", e)
    
    def start_continuous(self, check_interval: int = 60):
        """
        Start continuous scheduling loop (blocking)
        
        Args:
            check_interval: Seconds between schedule checks
        """
        try:
            self.logger.info(f"Starting continuous scheduler (check interval: {check_interval}s)")
            
            while True:
                self.run_pending()
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error("Scheduler error", e)
    
    def get_next_run(self, tag: Optional[str] = None) -> Optional[datetime]:
        """
        Get next scheduled run time
        
        Args:
            tag: Specific job tag (if None, returns earliest)
        
        Returns:
            Next run datetime or None
        """
        try:
            if tag:
                jobs = self.scheduler.get_jobs(tag)
                if jobs:
                    return jobs[0].next_run
            else:
                if self.scheduler.jobs:
                    return min(job.next_run for job in self.scheduler.jobs)
            
            return None
        except Exception as e:
            self.logger.error("Error getting next run time", e)
            return None
    
    def print_schedule(self):
        """Print current schedule"""
        try:
            jobs = self.scheduler.get_jobs()
            
            if not jobs:
                self.logger.info("No scheduled jobs")
                return
            
            self.logger.info("Current schedule:")
            for job in jobs:
                self.logger.info(f"  - {job.tag}: next run at {job.next_run}")
        except Exception as e:
            self.logger.error("Error printing schedule", e)


# Convenience function
def get_scheduler() -> TaskScheduler:
    """Get scheduler instance"""
    return TaskScheduler()
