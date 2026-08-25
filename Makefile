.PHONY: banner chips tech onsite atcoder build update fetch

banner:
	python3 scripts/render_banner.py

chips:
	python3 scripts/render_link_chips.py

tech:
	python3 scripts/render_tech_chips.py

onsite:
	python3 scripts/render_onsite_chart.py

atcoder-fetch:
	python3 scripts/fetch_atcoder_history.py

atcoder-chart:
	python3 scripts/render_atcoder_chart.py

# regenerate every image from current data, no network calls
build: banner chips tech onsite atcoder-chart
	python3 scripts/build_readme.py

# full refresh: also re-fetches AtCoder history over the network
update: banner chips tech onsite atcoder-fetch atcoder-chart
	python3 scripts/build_readme.py
