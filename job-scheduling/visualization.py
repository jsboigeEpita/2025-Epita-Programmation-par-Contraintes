"""
Visualization functions for job shop scheduling problems.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def print_solution(assignments, num_jobs, num_machines):
    """
    Print a text representation of the schedule.
    
    Args:
        assignments: Dictionary of assignments {(job_id, op_id): (start, end, machine)}
        num_jobs: Number of jobs
        num_machines: Number of machines
    """
    print("Solution:")
    
    # Sort assignments by job and operation
    for job_id in range(num_jobs):
        print(f"Job {job_id}:")
        # Get all operations for this job
        job_ops = [(op_id, data) for (j, op_id), data in assignments.items() if j == job_id]
        job_ops.sort()  # Sort by operation ID
        
        for op_id, (start, end, machine) in job_ops:
            print(f"  Operation {op_id}: Machine {machine}, Start: {start}, End: {end}, Duration: {end-start}")
    
    print("\nBy Machine:")
    for machine in range(num_machines):
        print(f"Machine {machine}:")
        # Get all operations for this machine
        machine_ops = [((j, op), data) for (j, op), data in assignments.items() if data[2] == machine]
        # Sort by start time
        machine_ops.sort(key=lambda x: x[1][0])
        
        for (job_id, op_id), (start, end, _) in machine_ops:
            print(f"  Job {job_id}, Op {op_id}: Start: {start}, End: {end}, Duration: {end-start}")

def visualize_advanced_schedule(instance, assignments, ai_insights=None):
    """
    Visualize the schedule with maintenance periods, due dates, and optional AI insights.
    
    Args:
        instance: Dictionary with problem instance data
        assignments: Dictionary of assignments {(job_id, op_id): (start, end, machine)}
        ai_insights: Optional string with AI-generated insights about the schedule
    """
    # Extract data from instance
    jobs_data = instance['jobs_data']
    maintenance_periods = instance['maintenance_periods']
    due_dates = instance['due_dates']
    num_jobs = instance['num_jobs']
    num_machines = instance['num_machines']
    
    # Calculate makespan
    makespan = max(end for (_, _), (_, end, _) in assignments.items())
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Colors for different jobs
    colors = plt.cm.tab20(np.linspace(0, 1, num_jobs))
    
    # Draw the operations on the chart
    for (job_id, op_id), (start, end, machine) in assignments.items():
        rect = patches.Rectangle(
            (start, machine), end - start, 0.8, 
            linewidth=1, edgecolor='black', 
            facecolor=colors[job_id], alpha=0.7
        )
        ax.add_patch(rect)
        ax.text(start + (end - start) / 2, machine + 0.4, f"J{job_id}-{op_id}", 
                ha='center', va='center', fontsize=8, color='black')
    
    # Add maintenance periods
    if maintenance_periods:
        for machine_id, start_time, duration in maintenance_periods:
            rect = patches.Rectangle(
                (start_time, machine_id), duration, 0.8, 
                linewidth=1, edgecolor='red', facecolor='gray', 
                alpha=0.6, hatch='///'
            )
            ax.add_patch(rect)
            ax.text(start_time + duration / 2, machine_id + 0.4, "MAINTENANCE", 
                    ha='center', va='center', fontsize=8, color='red')
    
    # Add due dates if available
    if due_dates:
        for job_id, due_date in due_dates.items():
            ax.axvline(x=due_date, color=colors[job_id], linestyle='--', alpha=0.5)
            ax.text(due_date, num_machines + 0.5, f"Due J{job_id}", 
                    rotation=90, ha='center', va='center', fontsize=8)
    
    # Identify and mark the bottleneck machine
    machine_load = {}
    for (_, _), (start, end, machine) in assignments.items():
        if machine not in machine_load:
            machine_load[machine] = 0
        machine_load[machine] += (end - start)
    
    bottleneck_machine = max(machine_load, key=machine_load.get) if machine_load else None
    if bottleneck_machine is not None:
        ax.text(-5, bottleneck_machine + 0.4, "⚠️ BOTTLENECK", fontsize=9, color='red')
    
    # Calculate job tardiness
    job_completion_times = {}
    job_tardiness = {}
    
    for (job_id, op_id), (start, end, _) in assignments.items():
        if job_id not in job_completion_times or end > job_completion_times[job_id]:
            job_completion_times[job_id] = end
    
    total_tardiness = 0
    for job_id, completion_time in job_completion_times.items():
        due_date = due_dates.get(job_id, float('inf'))
        tardiness = max(0, completion_time - due_date)
        job_tardiness[job_id] = tardiness
        total_tardiness += tardiness
    
    # Setup the plot
    ax.set_ylim(-0.5, num_machines + 1)
    ax.set_xlim(-10, makespan + 10)
    ax.set_yticks(range(num_machines))
    ax.set_yticklabels([f"Machine {i}" for i in range(num_machines)])
    ax.set_xlabel('Time')
    ax.set_title(f'Job Shop Schedule (Makespan: {makespan}, Tardiness: {total_tardiness})')
    ax.grid(True, alpha=0.3)
    
    # Add job legend
    legend_elements = [patches.Patch(facecolor=colors[j], edgecolor='black', alpha=0.7, label=f'Job {j}') 
                      for j in range(num_jobs)]
    legend_elements.append(patches.Patch(facecolor='gray', edgecolor='red', alpha=0.6, hatch='///', label='Maintenance'))
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Add AI insights if provided
    if ai_insights:
        # Truncate insights if they're too long
        max_lines = 8
        insights_lines = ai_insights.split('\n')
        if len(insights_lines) > max_lines:
            truncated_insights = '\n'.join(insights_lines[:max_lines-1]) + '\n...'
        else:
            truncated_insights = ai_insights
            
        # Position text in a box at the right side of the plot
        props = dict(boxstyle='round', facecolor='lightyellow', alpha=0.7)
        ax.text(1.02, 0.5, f"AI INSIGHTS:\n\n{truncated_insights}", 
                transform=ax.transAxes, fontsize=9,
                verticalalignment='center', bbox=props)
        
        fig.subplots_adjust(right=0.75)  # Make room for the insights box
    
    plt.tight_layout()
    plt.savefig('schedule.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig, ax