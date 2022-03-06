#!/bin/bash
dest_file={{ shares_path }}/unicloud-backup/unicloud-backup-$(date +%Y%d%m).tgz
tar czvf $dest_file /data/etc /data/ssh /data/unicloud.db /data/.ssh /data/.unison
cd {{ shares_path }}/unicloud-backup
rm -f `ls -t | awk 'NR>7'`