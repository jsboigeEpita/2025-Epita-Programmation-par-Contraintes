from typing import List, Dict, Optional, Any
from langchain_core.tools import tool
from pydantic import BaseModel
import logging
import io

from main import student_project_allocation


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("allocation_ai.log"), logging.StreamHandler()],
)
logger = logging.getLogger("allocation_ai")


class Item(BaseModel):
    id: int
    list: List[int]


class Item2(BaseModel):
    id: int
    number: int


@tool
def student_project_allocation_tool(
    students: List[int],
    projects: List[int],
    preferences: List[Item],
    project_capacities: List[Item2],
) -> str:
    """
    Run the student project allocation algorithm and generate an image of the allocation.
    """
    print("Executing student project allocation tool")
    preferences_2 = {pref.id: pref.list for pref in preferences}
    project_capacities_2 = {cap.id: cap.number for cap in project_capacities}

    allocation, benchmark_info = student_project_allocation(
        students, projects, preferences_2, project_capacities_2, []
    )

    text = benchmark_text_from_allocation(
        students,
        projects,
        preferences_2,
        project_capacities_2,
        allocation,
        benchmark_info,
    )
    return text


def generate_image_from_allocation(
    allocation: Optional[Dict[int, int]],
    benchmark_info: Dict[str, Any],
) -> Optional[io.BytesIO]:
    """
    Generate an image visualization of the allocation if one exists.
    Returns a BytesIO object with the image data, or None if no allocation exists.
    """
    logger.info(f"Generating image, allocation exists: {allocation is not None}")

    # If no allocation was found, return None early
    if not allocation:
        logger.warning("No allocation found, so no image will be generated.")
        return None

    best_algo = benchmark_info.get("best_algorithm")
    best_score = benchmark_info.get("best_score")

    # Generate visualization
    import matplotlib.pyplot as plt
    import networkx as nx
    import io

    # Create a graph representation of the allocation
    G = nx.Graph()
    plt.clf()
    for student, project in allocation.items():
        G.add_node(f"Student {student}", type="student")
        G.add_node(f"Project {project}", type="project")
        G.add_edge(f"Student {student}", f"Project {project}")

    # Visualize the graph
    pos = nx.spring_layout(
        G, k=0.5, iterations=50
    )  # Adjust k and iterations for better spacing
    student_nodes = [
        node for node, data in G.nodes(data=True) if data.get("type") == "student"
    ]
    project_nodes = [
        node for node, data in G.nodes(data=True) if data.get("type") == "project"
    ]

    plt.figure(figsize=(10, 8))  # Increase figure size for better readability
    nx.draw_networkx_nodes(
        G, pos, nodelist=student_nodes, node_color="skyblue", node_size=800
    )
    nx.draw_networkx_nodes(
        G, pos, nodelist=project_nodes, node_color="lightgreen", node_size=1200
    )
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")

    # Include best algorithm info in the title if available
    if best_algo and best_score is not None:
        plt.title(
            f"Student Project Allocation (Best: {best_algo}, Score: {best_score:.4f})"
        )
    else:
        plt.title("Student Project Allocation")

    plt.tight_layout()  # Adjust layout to prevent labels from overlapping

    # Convert the plot to an image in memory
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    # Store the image in the context
    logger.info("Successfully generated and stored the allocation image.")
    return buf


def benchmark_text_from_allocation(
    students: List[int],
    projects: List[int],
    preferences: Dict[int, List[int]],
    project_capacities: Dict[int, int],
    allocation: Optional[Dict[int, int]],
    benchmark_info: Dict[str, Dict[str, float]],
):
    # Build the response text
    text = ""

    # First add benchmarking information
    text += "## Algorithm Benchmarking\n\n"
    text += "| Algorithm | Score | Time (s) | Solution Found |\n"
    text += "|-----------|-------|----------|---------------|\n"

    for algo_name, results in benchmark_info.items():
        if algo_name not in ["best_algorithm", "best_score"]:
            score = results.get("score")
            time = results.get("time")
            solution = "Yes" if results.get("solution_found", False) else "No"

            score_display = f"{score:.4f}" if score is not None else "N/A"
            time_display = f"{time:.4f}" if time is not None else "N/A"

            text += f"| {algo_name} | {score_display} | {time_display} | {solution} |\n"

    best_algo = benchmark_info.get("best_algorithm")
    best_score = benchmark_info.get("best_score")

    if best_algo and best_score is not None:
        text += f"\nBest algorithm: **{best_algo}** with score {best_score:.4f}\n\n"
    else:
        text += "\nNo algorithm was able to find a valid solution.\n\n"

    if allocation:
        # Then add allocation details
        text += "## Allocation Results\n\n"
        text += "| Student | Project | Preference Rank |\n"
        text += "|---------|---------|----------------|\n"

        # Calculate preference satisfaction
        satisfied = 0
        total = len(students)

        for student in sorted(allocation.keys()):
            project = allocation[student]
            if student in preferences and project in preferences[student]:
                pref_idx = preferences[student].index(project) + 1  # 1-based rank
                rank_text = f"#{pref_idx}"
                satisfied += 1
            else:
                rank_text = "Not in preferences"

            text += f"| {student} | {project} | {rank_text} |\n"

        # Add summary of preference satisfaction
        if total > 0:
            satisfaction_rate = (satisfied / total) * 100
            text += f"\n### Preference Satisfaction Summary\n\n"
            text += f"- **Satisfaction Rate**: {satisfaction_rate:.1f}%\n"
            text += (
                f"- **Students with Preferred Projects**: {satisfied} out of {total}\n"
            )

            # Add preference distribution
            if satisfied > 0:
                text += "\n**Preference Distribution:**\n\n"
                rank_counts = {}
                for student, project in allocation.items():
                    if student in preferences and project in preferences[student]:
                        rank = preferences[student].index(project) + 1
                        rank_counts[rank] = rank_counts.get(rank, 0) + 1

                for rank in sorted(rank_counts.keys()):
                    count = rank_counts[rank]
                    percentage = (count / total) * 100
                    text += (
                        f"- Preference #{rank}: {count} students ({percentage:.1f}%)\n"
                    )
    else:
        text += "No valid allocation could be found with the given constraints."

    return text
