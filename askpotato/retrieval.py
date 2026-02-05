from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def handle_list_scenarios(cur) -> List[str]:
    """
    Get list of all scenario names
    
    Args:
        cur: Database cursor
        
    Returns:
        List of scenario names
    """
    try:
        cur.execute("SELECT name FROM scenarios ORDER BY created_at DESC")
        return [row["name"] for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching scenarios: {e}")
        return []


def handle_most_defects_scenario(cur) -> Optional[Dict]:
    """
    Find the scenario with the highest number of defects
    
    Args:
        cur: Database cursor
        
    Returns:
        Dict with scenario name and defect count, or None
    """
    try:
        # group by scenario and count defects
        cur.execute("""
            SELECT scenario_id, COUNT(*) AS defect_count
            FROM defects
            GROUP BY scenario_id
            ORDER BY defect_count DESC
            LIMIT 1
        """)
        result = cur.fetchone()

        if not result:
            return None

        # get the scenario name
        cur.execute(
            "SELECT name FROM scenarios WHERE id = ?",
            (result["scenario_id"],)
        )
        scenario = cur.fetchone()

        return {
            "name": scenario["name"],
            "defect_count": result["defect_count"]
        }
    except Exception as e:
        logger.error(f"Error finding scenario with most defects: {e}")
        return None


def handle_open_defects(cur) -> List[Dict]:
    """
    Get all defects that are still open
    
    Args:
        cur: Database cursor
        
    Returns:
        List of dicts with defect info
    """
    try:
        cur.execute("""
            SELECT d.title, d.reported_by, s.name as scenario_name
            FROM defects d
            JOIN scenarios s ON d.scenario_id = s.id
            WHERE d.status = 'Open'
            ORDER BY d.created_at DESC
        """)
        return [
            {
                "title": row["title"],
                "reported_by": row["reported_by"],
                "scenario": row["scenario_name"]
            }
            for row in cur.fetchall()
        ]
    except Exception as e:
        logger.error(f"Error fetching open defects: {e}")
        return []


def handle_failed_steps(cur) -> List[Dict]:
    """
    Find all steps marked as Failed
    
    Args:
        cur: Database cursor
        
    Returns:
        List of failed steps with scenario info
    """
    try:
        cur.execute("""
            SELECT st.step_name, st.step_number, sc.name as scenario_name
            FROM steps st
            JOIN scenarios sc ON st.scenario_id = sc.id
            WHERE st.status = 'Failed'
            ORDER BY sc.name, st.step_number
        """)
        return [
            {
                "step_name": row["step_name"],
                "step_number": row["step_number"],
                "scenario": row["scenario_name"]
            }
            for row in cur.fetchall()
        ]
    except Exception as e:
        logger.error(f"Error fetching failed steps: {e}")
        return []


def handle_no_proof_steps(cur) -> List[Dict]:
    """
    Find steps that don't have any proof files uploaded
    Uses LEFT JOIN to find orphaned steps
    
    Args:
        cur: Database cursor
        
    Returns:
        List of steps missing proof
    """
    try:
        cur.execute("""
            SELECT s.step_name, s.step_number, sc.name as scenario_name
            FROM steps s
            JOIN scenarios sc ON s.scenario_id = sc.id
            LEFT JOIN proofs p
              ON s.scenario_id = p.scenario_id
             AND s.step_number = p.step_number
            WHERE p.id IS NULL
            ORDER BY sc.name, s.step_number
        """)
        return [
            {
                "step_name": row["step_name"],
                "step_number": row["step_number"],
                "scenario": row["scenario_name"]
            }
            for row in cur.fetchall()
        ]
    except Exception as e:
        logger.error(f"Error fetching steps without proof: {e}")
        return []
