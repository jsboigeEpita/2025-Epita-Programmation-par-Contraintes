"""
AI Enhancement functions for Job Shop Scheduling using OpenAI API.
"""

import openai
import json
import os

# Check if OPENAI_API_KEY is set in environment variables
if not os.environ.get('OPENAI_API_KEY'):
    print("Warning: OPENAI_API_KEY environment variable not set. AI features will not work.")

def get_ai_parameter_suggestions(instance):
    """
    Get optimization parameter suggestions from OpenAI.
    
    Args:
        instance: Dictionary containing problem instance data
    
    Returns:
        Dictionary with recommended parameters or None if API call fails
    """
    try:
        client = openai.OpenAI()
        
        # Extract key problem characteristics
        num_jobs = instance.get('num_jobs', 0)
        num_machines = instance.get('num_machines', 0)
        has_maintenance = instance.get('maintenance_periods') is not None and len(instance.get('maintenance_periods', [])) > 0
        has_due_dates = instance.get('due_dates') is not None
        
        prompt = f"""
        As an operations research expert, suggest parameters for a job shop scheduling problem with:
        - {num_jobs} jobs
        - {num_machines} machines
        - Maintenance periods: {"Yes" if has_maintenance else "No"}
        - Due dates: {"Yes" if has_due_dates else "No"}
        
        Return a JSON object with these parameters:
        - makespan_weight: Weight for makespan in objective function (1-1000)
        - tardiness_weight: Weight for tardiness in objective function (1-1000)
        
        Return only valid JSON with no explanations. For example:
        {{
          "makespan_weight": 5,
          "tardiness_weight": 500
        }}
        """
        
        # Try using JSON mode first, if that fails, fall back to regular completion
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in operations research."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
        except Exception as e:
            # Fall back to regular completion without response_format
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in operations research. You must respond with only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
        
        try:
            # Try to parse the response as JSON
            parameters = json.loads(response.choices[0].message.content)
            return parameters
        except json.JSONDecodeError:
            print("Warning: Could not parse AI response as JSON")
            return None
            
    except Exception as e:
        print(f"Warning: AI parameter suggestion failed: {e}")
        return None


def analyze_solution(instance, assignments, makespan, tardiness):
    """
    Analyze the scheduling solution and provide improvement suggestions.
    
    Args:
        instance: Dictionary containing problem instance data
        assignments: Dictionary of task assignments
        makespan: The makespan of the solution
        tardiness: The total tardiness of the solution
    
    Returns:
        String with analysis and suggestions
    """
    try:
        client = openai.OpenAI()
        
        # Calculate job completion times and tardiness
        job_completion = {}
        job_tardiness = {}
        
        for (job_id, op_id), (start, end, _) in assignments.items():
            if job_id not in job_completion or end > job_completion[job_id]:
                job_completion[job_id] = end
                
        for job_id, completion_time in job_completion.items():
            due_date = instance.get('due_dates', {}).get(job_id, float('inf'))
            job_tardiness[job_id] = max(0, completion_time - due_date)
        
        # Find machine with most load
        machine_load = {}
        for (_, _), (start, end, machine) in assignments.items():
            if machine not in machine_load:
                machine_load[machine] = 0
            machine_load[machine] += end - start
            
        bottleneck_machine = max(machine_load, key=machine_load.get) if machine_load else None
        
        # Create summary for AI
        solution_summary = {
            "num_jobs": instance.get('num_jobs', 0),
            "num_machines": instance.get('num_machines', 0),
            "makespan": makespan,
            "total_tardiness": tardiness,
            "late_jobs": sum(1 for t in job_tardiness.values() if t > 0),
            "bottleneck_machine": bottleneck_machine,
            "bottleneck_load": machine_load.get(bottleneck_machine, 0) if bottleneck_machine is not None else 0,
        }
        
        prompt = f"""
        Analyze this job shop scheduling solution:
        
        {json.dumps(solution_summary, indent=2)}
        
        Provide:
        1. A brief assessment of the solution quality
        2. Three specific suggestions to improve this schedule
        3. One insight about the bottleneck machine
        
        Keep your response concise and practical.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in operations research."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Warning: Solution analysis failed: {e}")
        return "AI analysis unavailable. Check your OpenAI API key and connection."


def explain_schedule(instance, assignments, makespan, tardiness):
    """
    Generate a natural language explanation of the schedule.
    
    Args:
        instance: Dictionary containing problem instance data
        assignments: Dictionary of task assignments
        makespan: The makespan of the solution
        tardiness: The total tardiness of the solution
    
    Returns:
        String with natural language explanation
    """
    try:
        client = openai.OpenAI()
        
        # Create a simple text representation of the schedule
        schedule_text = f"Schedule overview:\n"
        schedule_text += f"- Total makespan: {makespan}\n"
        schedule_text += f"- Total tardiness: {tardiness}\n"
        
        # Add information about job completion times
        job_completion = {}
        for (job_id, op_id), (start, end, machine) in assignments.items():
            if job_id not in job_completion or end > job_completion[job_id]:
                job_completion[job_id] = end
        
        schedule_text += "\nJob completion times:\n"
        for job_id, completion_time in sorted(job_completion.items()):
            due_date = instance.get("due_dates", {}).get(job_id, "N/A")
            tardy = max(0, completion_time - due_date) if due_date != "N/A" else "N/A"
            schedule_text += f"- Job {job_id}: Completed at t={completion_time}, Due date: {due_date}, Tardiness: {tardy}\n"
        
        # Create the prompt for GPT
        prompt = f"""
        As a manufacturing operations expert, explain this job shop schedule in clear language:
        
        {schedule_text}
        
        Provide a concise explanation that addresses:
        1. Overall schedule quality
        2. Any late jobs and their impact
        3. One specific recommendation for improvement
        
        Your explanation should be clear and helpful for a production manager.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in manufacturing operations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Warning: Schedule explanation failed: {e}")
        return "AI explanation unavailable. Check your OpenAI API key and connection."