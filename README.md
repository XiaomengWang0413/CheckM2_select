# CheckM2_select
~~~
python filter_genomes_and_copy.py -h
~~~

~~~
python filter_genomes_and_copy.py \
    -i /path/to/checkm_folder/quality_report.tsv \
    -s /path/to/genomes_folder \
    -d /path/to/selected_genomes
~~~
##使用硬链接（节省空间）
~~~
python filter_genomes_and_copy.py -i report.tsv -s genomes -d good_genomes --copy-mode link
~~~
##预览（不实际复制）
~~~
python filter_genomes_and_copy.py -i report.tsv -s genomes -d good_genomes --dry-run
~~~
