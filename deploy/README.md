sudo cp deploy/blog.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable blog
sudo systemctl restart blog