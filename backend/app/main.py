from datetime import datetime
from config.settings import NUM_PROJECTS_TO_SUMMARIZE, DAYS_TO_SKIP
from .scraper import scrape_github_trending
from .database import ProjectDatabase
from .summarizer import get_summary_for_single_project, get_overview_intro
from .file_writer import save_summary_files
from config.logging_config import get_logger
import time

# 创建日志记录器
logger = get_logger('main', 'INFO')

def job():
    logger.info(f"Starting new job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = ProjectDatabase()
    
    all_trending_repos = scrape_github_trending()
    if not all_trending_repos:
        logger.info("Job finished: no data scraped.")
        return

    snapshot_date = datetime.now().date()
    logger.info(f"Ingesting {len(all_trending_repos)} projects for date: {snapshot_date.isoformat()}")
    
    # Add rank to each project
    for i, repo_data in enumerate(all_trending_repos):
        repo_data['rank'] = i + 1
        
    # Use the new batch insertion method
    db.add_trending_snapshots(all_trending_repos, snapshot_date)
    
    logger.info(f"Successfully ingested {len(all_trending_repos)} snapshots into the database.")

    # Get project names that have been summarized recently
    existing_project_names = db.get_all_summarized_project_names(DAYS_TO_SKIP)
    
    repos_to_summarize = []
    logger.info(f"Filtering for {NUM_PROJECTS_TO_SUMMARIZE} new projects to summarize...")
    for repo in all_trending_repos:
        if repo['name'] not in existing_project_names:
            repos_to_summarize.append(repo)
        if len(repos_to_summarize) >= NUM_PROJECTS_TO_SUMMARIZE:
            logger.info(f"Found {len(repos_to_summarize)} new projects to summarize.")
            break

    if not repos_to_summarize:
        logger.info("No new projects to summarize today.")
    else:
        logger.info(f"Summarizing {len(repos_to_summarize)} new projects...")
        from app.summarizer import extract_tech_domain
        individual_summaries = []
        for project in repos_to_summarize:
            summary = get_summary_for_single_project(project)
            if summary:
                individual_summaries.append(summary)
                # 提取技术领域并添加到项目数据
                tech_domain = extract_tech_domain(summary)
                project['tech_domain'] = tech_domain
                logger.info(f"Tech domain for {project['name']}: {tech_domain}")
                # Also add it to the legacy summarized_projects table
                db.add_summarized_project(project)
                time.sleep(1)
            else:
                logger.warning(f"Failed to summarize '{project['name']}'. Skipping this project.")

        if individual_summaries:
            intro = get_overview_intro(repos_to_summarize)
            final_report = intro + "\n\n" + "\n\n---\n\n".join(individual_summaries)
            
            save_summary_files(final_report)
            logger.info(f"Successfully saved report for {len(repos_to_summarize)} projects.")

    logger.info(f"Job finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
