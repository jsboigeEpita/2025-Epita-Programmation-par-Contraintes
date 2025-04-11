"""
Heuristic functions for Job Shop Scheduling optimization.
"""

import openai
import json
import time

def apply_standard_heuristic(model, all_tasks, jobs_data, due_dates, heuristic_name="SPT"):
    """
    Apply a standard heuristic to guide the CP-SAT solver's search.
    
    Args:
        model: The CP-SAT model
        all_tasks: Dictionary of task variables {(job_id, op_id): (start_var, end_var, interval_var)}
        jobs_data: List of jobs with their operations
        due_dates: Dictionary of due dates for each job
        heuristic_name: Name of the heuristic to apply ("SPT", "EDD", "CR", "MOR")
    
    Returns:
        Modified model with heuristic applied
    """
    # Calculate job priorities based on the selected heuristic
    job_priorities = {}
    
    for job_id in range(len(jobs_data)):
        if heuristic_name == "SPT":  # Shortest Processing Time
            priority = sum(op[1] for op in jobs_data[job_id])
            
        elif heuristic_name == "EDD":  # Earliest Due Date
            priority = due_dates.get(job_id, float('inf'))
            
        elif heuristic_name == "CR":  # Critical Ratio (due date / processing time)
            processing_time = sum(op[1] for op in jobs_data[job_id])
            if processing_time > 0:
                priority = due_dates.get(job_id, float('inf')) / processing_time
            else:
                priority = float('inf')
                
        elif heuristic_name == "MOR":  # Most Operations Remaining (negative)
            priority = -len(jobs_data[job_id])
            
        else:  # Default to SPT
            priority = sum(op[1] for op in jobs_data[job_id])
            
        job_priorities[job_id] = priority
    
    # Sort jobs by priority (lower value = higher priority)
    sorted_jobs = sorted(job_priorities.keys(), key=lambda j: job_priorities[j])
    
    # Add hints to the model to guide the search
    for rank, job_id in enumerate(sorted_jobs):
        for op_id in range(len(jobs_data[job_id])):
            # Get the start variable for this operation
            start_var = all_tasks[(job_id, op_id)][0]
            
            # Add a hint with a weight based on the job's priority
            # This encourages the solver to schedule high-priority jobs earlier
            model.AddHint(start_var, rank * 10)
    
    return model


def generate_ai_heuristic(instance):
    """
    Generate a custom priority rule using OpenAI based on problem characteristics.
    
    Args:
        instance: Dictionary containing problem instance data
    
    Returns:
        String containing the heuristic rule name or formula to use
    """
    try:
        client = openai.OpenAI()
        
        # Extract key problem characteristics
        jobs_data = instance.get('jobs_data', [])
        num_jobs = instance.get('num_jobs', 0)
        num_machines = instance.get('num_machines', 0)
        has_maintenance = instance.get('maintenance_periods') is not None and len(instance.get('maintenance_periods', [])) > 0
        has_due_dates = instance.get('due_dates') is not None
        
        # Calculate average processing time per job
        processing_times = []
        for job in jobs_data:
            job_time = sum(op[1] for op in job)
            processing_times.append(job_time)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Calculate machine loads
        machine_load = {}
        for job in jobs_data:
            for machine, processing_time in job:
                if machine not in machine_load:
                    machine_load[machine] = 0
                machine_load[machine] += processing_time
        
        bottleneck_machine = max(machine_load.keys(), key=lambda m: machine_load[m]) if machine_load else None
        
        # Create problem summary for AI
        problem_summary = {
            "num_jobs": num_jobs,
            "num_machines": num_machines,
            "avg_processing_time": avg_processing_time,
            "max_processing_time": max(processing_times) if processing_times else 0,
            "min_processing_time": min(processing_times) if processing_times else 0,
            "processing_time_variance": max(processing_times) - min(processing_times) if processing_times else 0,
            "bottleneck_machine": bottleneck_machine,
            "bottleneck_load": machine_load.get(bottleneck_machine, 0) if bottleneck_machine is not None else 0,
            "has_maintenance": has_maintenance,
            "has_due_dates": has_due_dates,
        }
        
        prompt = f"""
        As an expert in scheduling algorithms, analyze this job shop scheduling problem:
        
        {json.dumps(problem_summary, indent=2)}
        
        Based on these characteristics, which of these standard priority rules would work best:
        1. SPT (Shortest Processing Time) - prioritize jobs with shortest total processing time
        2. EDD (Earliest Due Date) - prioritize jobs with earliest due dates
        3. CR (Critical Ratio) - prioritize jobs with lowest (due date / processing time) ratio
        4. MOR (Most Operations Remaining) - prioritize jobs with the most operations
        
        Select exactly one of: "SPT", "EDD", "CR", or "MOR" and explain why you chose it.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in operations research."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        # Extract just the rule name from the response
        answer = response.choices[0].message.content
        
        # Try to extract the heuristic name (look for SPT, EDD, CR, or MOR)
        import re
        rule_match = re.search(r'\b(SPT|EDD|CR|MOR)\b', answer)
        
        if rule_match:
            selected_rule = rule_match.group(0)
            print(f"AI selected heuristic: {selected_rule}")
            print(f"Reasoning: {answer}")
            return selected_rule
        else:
            # If no match is found, default to SPT
            print("Could not determine AI's heuristic choice, defaulting to SPT.")
            return "SPT"
            
    except Exception as e:
        print(f"Warning: AI heuristic generation failed: {e}")
        print("Using default SPT heuristic instead.")
        return "SPT"