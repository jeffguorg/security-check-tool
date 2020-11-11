Linux实现所需的配置文件和脚本。需要安装时放置到对应路径中

> 生成单文件脚本：
```bash
fakeroot
cat > install.sh << EOF
#!/usr/bin/env bash

tail -n1 $0 | base64 -d | tar xzv -C /

exit 0
# rootfs
EOF
tar czv -C . | bash64 -w 0 >> install.sh
chmod +x install.sh
```
