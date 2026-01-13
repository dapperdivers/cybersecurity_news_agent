#!/bin/bash
# Quick test: Fetch last 24 hours of cybersecurity news

echo "🚀 Quick test: Fetching news from last 24 hours..."
echo ""

docker-compose exec -T cybersec-agent /usr/local/bin/entrypoint.sh bash -c 'echo "Fetch cybersecurity news from the last 24 hours and provide a brief summary with the top 5 most important items" | claude --agent news-aggregator --dangerously-skip-permissions'
