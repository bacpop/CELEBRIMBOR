import argparse


def get_options():
    description = 'Matches pangenome assignments from CELEBRIMBOR pre and post simulation (assumes remove_sequence.py has been run).'
    parser = argparse.ArgumentParser(description=description,
                                     prog='python analyse_celebrimbor_simulation.py')

    IO = parser.add_argument_group('Input/Output options')
    IO.add_argument('--matched-genes',
                    default=None,
                    required=True,
                    help='.tsv file generated from match_genes.py')
    IO.add_argument('--cgt-pre',
                    default=None,
                    required=True,
                    help='cgt_output.txt file generated by CELEBRIMBOR for PRE-simulation dataset.')
    IO.add_argument('--cgt-post',
                default=None,
                required=True,
                help='cgt_output.txt file generated by CELEBRIMBOR for POST-simulation dataset.')
    IO.add_argument('--checkm-pre',
            default=None,
            required=True,
            help='checkm_out.tsv file generated by CELEBRIMBOR for PRE-simulation dataset.')
    IO.add_argument('--checkm-post',
            default=None,
            required=True,
            help='checkm_out.tsv file generated by CELEBRIMBOR for POST-simulation dataset.')
    IO.add_argument('--pan-pre',
            default=None,
            required=True,
            help='pangenome_summary.tsv file generated by CELEBRIMBOR for PRE-simulation dataset.')
    IO.add_argument('--pan-post',
            default=None,
            required=True,
            help='pangenome_summary.tsv file generated by CELEBRIMBOR for POST-simulation dataset.')
    IO.add_argument('--mmseqs-pre',
            default=None,
            required=True,
            help='mmseqs_cluster.sorted.tsv file generated by CELEBRIMBOR for PRE-simulation dataset.')
    IO.add_argument('--mmseqs-post',
            default=None,
            required=True,
            help='mmseqs_cluster.sorted.tsv file generated by CELEBRIMBOR for POST-simulation dataset.')
    IO.add_argument('--outpref',
                    default="celebrimbor_results",
                    help='Output prefix. Default = "celebrimbor_results"')

    return parser.parse_args()

def main():
    options = get_options()
    gene_matches = options.matched_genes
    cgt_pre = options.cgt_pre
    cgt_post = options.cgt_post
    checkm_pre = options.checkm_pre
    checkm_post = options.checkm_post
    pan_pre = options.pan_pre
    pan_post = options.pan_post
    mmseqs_pre = options.mmseqs_pre
    mmseqs_post = options.mmseqs_post
    outpref = options.outpref

    # testing
    # gene_matches = "data/cgt_test/matched_genes.tsv"
    # cgt_pre = "data/cgt_test/cgt_output_ori.txt"
    # cgt_post = "data/cgt_test/cgt_output_sim.txt"
    # checkm_pre = "data/cgt_test/checkm_out_ori.tsv"
    # checkm_post = "data/cgt_test/checkm_out_sim.tsv"
    # pan_pre = "data/cgt_test/pangenome_summary_ori.tsv"
    # pan_post = "data/cgt_test/pangenome_summary_sim.tsv"
    # mmseqs_pre = "data/cgt_test/mmseqs_cluster_ori.sorted.tsv"
    # mmseqs_post = "data/cgt_test/mmseqs_cluster_sim.sorted.tsv"
    # outpref = "data/cgt_test/celebrimbor_results"

    # get matched genes, key is gene from simulation
    matched_genes = {}
    with open(gene_matches, "r") as f:
        next(f)
        for line in f:
            split_line = line.rstrip().split("\t")
            matched_genes[split_line[1]] = split_line[0]
    

    # read in clusters for pre
    gene_to_cluster_pre = {}
    cluster_to_gene_pre = set()
    with open(mmseqs_pre, "r") as f:
        for line in f:
            split_line = line.rstrip().split("\t")
            #key is gene, item is cluster
            gene_to_cluster_pre[split_line[1]] = split_line[0]

            # key is cluster, item is list of genes
            # if split_line[0] not in cluster_to_gene_pre:
            #     cluster_to_gene_pre[split_line[0]] = []
            cluster_to_gene_pre.add(split_line[0])#.append(split_line[1])
    
    # read in clusters for post
    #gene_to_cluster_post = {}
    cluster_to_gene_post = {}
    with open(mmseqs_post, "r") as f:
        for line in f:
            split_line = line.rstrip().split("\t")
            #key is gene, item is cluster
            #gene_to_cluster_post[split_line[1]] = split_line[0]

            # key is cluster, item is list of genes
            if split_line[0] not in cluster_to_gene_post:
                cluster_to_gene_post[split_line[0]] = []
            cluster_to_gene_post[split_line[0]].append(split_line[1])

    # map clusters between pre and post sim (first is original, second is simulated)
    mapped_clusters = []
    for post_cluster, post_gene_list in cluster_to_gene_post.items():
        found = False
        for gene in post_gene_list:
            matched_gene = matched_genes[gene]
            
            # avoid none-assignments
            if matched_gene is None:
                continue

            # determine mapped cluster
            if matched_gene in gene_to_cluster_pre:
                # delete cluster from gene_to_cluster_pre
                pre_cluster = gene_to_cluster_pre[matched_gene]

                # delete cluster from gene_to_cluster_pre. 
                # May be case multiple new clusters map to old cluster.
                cluster_to_gene_pre.discard(pre_cluster)

                # append paired clusters
                mapped_clusters.append((pre_cluster, post_cluster))

                found = True
                break
        
        # no cluster found
        if found == False:
            mapped_clusters.append(("None", post_cluster))

    # determine which pre clusters have no match
    for pre_cluster in cluster_to_gene_pre:
        mapped_clusters.append((pre_cluster, "None"))

    # remove stored information
    cluster_to_gene_post.clear()
    matched_genes.clear()
    gene_to_cluster_pre.clear()
    cluster_to_gene_pre.clear()

    # parse cgt outputs
    cgt_pre_dict = {}
    with open(cgt_pre, "r") as f:
        next(f)
        for line in f:
            split_line = line.rstrip().split("\t")
            # key is gene, first entry is count, second is frequency label
            cgt_pre_dict[split_line[0]] = (split_line[1], split_line[2])
    
    cgt_post_dict = {}
    with open(cgt_post, "r") as f:
        next(f)
        for line in f:
            split_line = line.rstrip().split("\t")
            # key is gene, first entry is count, second is frequency label
            cgt_post_dict[split_line[0]] = (split_line[1], split_line[2])

    # parse checkm outputs
    checkm_pre_dict = {}
    with open(checkm_pre, "r") as f:
        next(f)
        for line in f:
            split_line = line.rstrip().split("\t")
            # key is gene, first entry is completeness
            checkm_pre_dict[split_line[0]] = split_line[11]
    
    checkm_post_dict = {}
    with open(checkm_post, "r") as f:
        next(f)
        for line in f:
            split_line = line.rstrip().split("\t")
            # key is gene, first entry is completeness
            checkm_post_dict[split_line[0]] = split_line[11]

    # parse pangenome summary
    pan_pre_dict = {}
    with open(pan_pre, "r") as f:
        for line in f:
            split_line = line.rstrip().split("\t")
            # key is gene, first entry is frequency, second is frequency bin
            pan_pre_dict[split_line[0]] = (split_line[2], split_line[3])
    
    pan_post_dict = {}
    with open(pan_post, "r") as f:
        for line in f:
            split_line = line.rstrip().split("\t")
            # key is gene, first entry is frequency, second is frequency bin
            pan_post_dict[split_line[0]] = (split_line[2], split_line[3])
    

    # merge all together:
    final_output = []
    for pre_cluster, post_cluster in mapped_clusters:
        cluster_dict = {}

        if pre_cluster != "None":
            # get completeness
            pre_completeness_real = 100.0
            pre_completeness_est = checkm_pre_dict[pre_cluster.rsplit('_', 1)[0]]

            # get cgt estimates
            pre_cgt_tuple = cgt_pre_dict[pre_cluster]
            pre_count = pre_cgt_tuple[0]
            pre_pan_est = pre_cgt_tuple[1]

            # get pangenome estimates
            pre_pan_tuple = pan_pre_dict[pre_cluster]
            pre_freq = pre_pan_tuple[0]
            pre_pan_calc = pre_pan_tuple[1]
        else:
            pre_completeness_real = "NA"
            pre_completeness_est = "NA"
            pre_count = "NA"
            pre_pan_est = "NA"
            pre_freq = "NA"
            pre_pan_calc = "NA"
        
        if post_cluster != "None":
            post_completness_real = float(post_cluster.split("_")[-2]) * 100
            post_completeness_est = checkm_post_dict[post_cluster.rsplit('_', 1)[0]]

            # get cgt estimates
            post_cgt_tuple = cgt_post_dict[post_cluster]
            post_count = post_cgt_tuple[0]
            post_pan_est = post_cgt_tuple[1]

            # get pangenome estimates
            post_pan_tuple = pan_post_dict[post_cluster]
            post_freq = post_pan_tuple[0]
            post_pan_calc = post_pan_tuple[1]
        else:
            post_completness_real = "NA"
            post_completeness_est = "NA"
            post_count = "NA"
            post_pan_est = "NA"
            post_freq = "NA"
            post_pan_calc = "NA"
        
        cluster_dict["Pre_sim_cluster"] = pre_cluster
        cluster_dict["Post_sim_cluster"] = post_cluster
        
        cluster_dict["Pre_sim_completeness_real"] = pre_completeness_real
        cluster_dict["Post_sim_completeness_real"] = post_completness_real
        
        cluster_dict["Pre_sim_completeness_est"] = pre_completeness_est
        cluster_dict["Post_sim_completeness_est"] = post_completeness_est

        cluster_dict["Pre_sim_cgt_count"] = pre_count
        cluster_dict["Post_sim_cgt_count"] = post_count

        cluster_dict["Pre_sim_cgt_compartment"] = pre_pan_est
        cluster_dict["Post_sim_cgt_compartment"] = post_pan_est

        cluster_dict["Pre_sim_freq"] = pre_freq
        cluster_dict["Post_sim_freq"] = post_freq

        cluster_dict["Pre_sim_freq_compartment"] = pre_pan_calc
        cluster_dict["Post_sim_freq_compartment"] = post_pan_calc

        final_output.append(cluster_dict)

    # output completeness file
    with open(outpref + ".tsv", "w+") as f:
        f.write("Pre_sim_cluster\tPost_sim_cluster\tPre_sim_completeness_real\tPost_sim_completeness_real\tPre_sim_completeness_est\tPost_sim_completeness_est\tPre_sim_cgt_count\tPost_sim_cgt_count \
                \tPre_sim_cgt_compartment\tPost_sim_cgt_compartment\tPre_sim_freq\tPost_sim_freq\tPre_sim_freq_compartment\tPost_sim_freq_compartment\n")
        for entry in final_output:
            f.write(entry["Pre_sim_cluster"] + "\t" + entry["Post_sim_cluster"] + "\t" + str(entry["Pre_sim_completeness_real"]) + "\t" + str(entry["Post_sim_completeness_real"]) 
                    + "\t" + str(entry["Pre_sim_completeness_est"]) + "\t" + str(entry["Post_sim_completeness_est"]) + "\t" + entry["Pre_sim_cgt_count"] + "\t" + entry["Post_sim_cgt_count"] 
                    + "\t" + entry["Pre_sim_cgt_compartment"] + "\t" + entry["Post_sim_cgt_compartment"] + "\t" + entry["Pre_sim_freq"] + "\t" + entry["Post_sim_freq"] + "\t" + entry["Pre_sim_freq_compartment"] 
                    + "\t" + entry["Post_sim_freq_compartment"] + "\n")
            

if __name__ == "__main__":
    main()