# JOB CRAWLER

- Inside loopcv_job_crawler:
    - docker build -f Dockerfile.indeed --tag IndeedJobCrawler:1.0 .
    
    - docker build -f Dockerfile.linkedin --tag LinkedinJobCrawler:1.0 .
    
    - docker run --publish 8000:8000 --detach --name ijc IndeedJobCrawler:1.0
    
    - docker run --publish 8000:8000 --detach --name ljc LinkedinJobCrawler:1.0
    
 - Hit browser: http://127.0.0.1:8000/docs

> Notes
>- publish: forward traffic incoming on the host’s port 8000, to the container’s ports 8000 and 8080.
>- detach: run this container in the background.
>- name: specifies a name with which you can refer to your container in subsequent commands.