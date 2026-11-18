# Copilot progressive engineering design

Read [DESIGN.md](DESIGN.md) for the proposed architecture and implementation sequence covering RAG, observability, Git, Jenkins and deployment. Use [BUILD_TRACKER.md](BUILD_TRACKER.md) as the working progress record.

The [Windows Jenkinsfile example](examples/Jenkinsfile.windows.ci) is a reviewed starting point for a future offline CI job. It is not installed as a root Jenkinsfile, configured on Jenkins or validated by the Jenkins controller yet.

Start with M00 and M01, preserving the running local application on API port 8082 and UI port 8501. Jenkins remains on port 8080. Source data, credentials, application behaviour and running services are unchanged by adding these design files.
