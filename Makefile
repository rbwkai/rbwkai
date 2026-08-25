.PHONY: banner stats chart build update fetch

banner:
	python3 scripts/render_banner.py

stats:
	python3 scripts/fetch_github_stats.py
	python3 scripts/render_stats_card.py

chart:
	python3 scripts/render_onsite_chart.py

# regenerate every image from current data, but don't hit the GitHub API
build: banner chart
	python3 scripts/build_readme.py

# full refresh: hits the GitHub API, then rebuilds everything
update: banner stats chart
	python3 scripts/build_readme.py
