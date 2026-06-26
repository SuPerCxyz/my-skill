# Decompression

Use this file only when the input is a `.eslog` bundle that still needs decompression. If the user already provides an extracted `ecs.*` directory, skip to [directory-map.md](directory-map.md) and [analysis-playbook.md](analysis-playbook.md).

## eslog File Format

EasyStack diagnostic logs are distributed as password-protected `.eslog` files. The decompression is multi-stage:

```
.eslog file (password: easycloud)
  → nested .eslog.[N] archive
    → .tar archive
      → .log.gz files (auto-decompressed)
        → plain .log files
```

## Decompress Script

Save this as `decompress_eslog.sh` in the directory containing `.eslog` files:

```bash
#!/bin/bash

set -x

TMP_DIR1="./tmp_unzip_stage1"
TMP_DIR2="./tmp_unzip_stage2"
mkdir -p "$TMP_DIR1" "$TMP_DIR2"

for file in `ls | egrep 'ecs.*eslog'`; do
    echo "开始解压 $file"
    unzip -P "easycloud" -o $file -d "$TMP_DIR1" 2>/dev/null || {
        echo "密码错误或文件损坏"
        exit 1
    }
done

echo "解压加密日志解压后的eslog"
find "$TMP_DIR1" -type f -name "ecs.*eslog.[0-9]" | while read nested_zip; do
    unzip -j -o "$nested_zip" -d "$TMP_DIR2"
done

echo "正在解压tar格式文件..."
find "$TMP_DIR2" -type f -name "ecs.*tar" | while read tar_file; do
    tar -xvf "$tar_file" -C ./
done

rm -rf "$TMP_DIR1" "$TMP_DIR2"

find . -maxdepth 5 -name "*.log.gz" -print0 | xargs -0 gunzip
```

## Output

```
ecs.<hostname>.<date>.<N>/          ← host-level directory (may have multiple)
├── alcubierre/
├── ceph/
├── ceph-k8s/
├── cloud-products/
├── ecas/
├── ecms/
├── ems/
├── kubernetes/
├── libvirt/
├── openstack/
├── os/
└── others/
```
