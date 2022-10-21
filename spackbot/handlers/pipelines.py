# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import spackbot.helpers as helpers

from spackbot.workers import (
    run_pipeline_task,
    report_rebuild_failure,
    get_queue,
    TASK_QUEUE_SHORT,
    WORKER_JOB_TIMEOUT,
)

logger = helpers.get_logger(__name__)


async def run_pipeline_rebuild_all(event, gh, **kwargs):
    """
    Run a pipeline that will force-rebuild everything from source
    """
    job_metadata = {
        "post_comments_url": event.data["issue"]["comments_url"],
        "rebuild_everything": True,
        "token": kwargs["token"],
    }

    task_q = get_queue(TASK_QUEUE_SHORT)
    scheduled_job = task_q.enqueue(
        run_pipeline_task,
        event,
        job_timeout=WORKER_JOB_TIMEOUT,
        meta=job_metadata,
        on_failure=report_rebuild_failure,
    )
    logger.info(f"Rebuild everything job enqueued: {scheduled_job.id}")


async def run_pipeline(event, gh, **kwargs):
    """
    Make a request to re-run a pipeline.
    """
    job_metadata = {
        "post_comments_url": event.data["issue"]["comments_url"],
        "token": kwargs["token"],
    }

    task_q = get_queue(TASK_QUEUE_SHORT)
    scheduled_job = task_q.enqueue(
        run_pipeline_task,
        event,
        job_timeout=WORKER_JOB_TIMEOUT,
        meta=job_metadata,
        on_failure=report_rebuild_failure,
    )
    logger.info(f"Run pipeline job enqueued: {scheduled_job.id}")
