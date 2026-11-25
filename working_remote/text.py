https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3

(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457467  red rx_E09_analy  4475918  R      17:20 1-23:42:40   1  16       N/A 128G hpctpa3pc0003
          22457666  red  public_flow  4475918  R       4:19 6-23:55:41   1   4       N/A   8G hpctpa3pc0035
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ sacct -X -j 22457666,22457467 -o JobID,JobName%36,State%24,ExitCode,Elapsed
PUBLIC_RUN_TAG/cJobID                                     JobName                    State ExitCode    Elapsed
------------ ------------------------------------ ------------------------ -------- ----------
22457467                           rx_E09_analyze                  RUNNING      0:0   00:18:59
22457666                              public_flow                COMPLETED      0:0   00:04:38
ontroller.22457666.log"
if [[ -f "$log" ]]; then
  tail -n 40 "$log"
fi(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ log="$TEST_LOG_DIR/$PUBLIC_RUN_TAG/ctroller.22457666.log"
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ if [[ -f "$log" ]]; then
>   tail -n 40 "$log"
> fi
Downloaded/validated 2 pinned CRI iAtlas ICI files in /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/downloads/iatlas_ici
Staged validated CRI iAtlas inputs for Kim, Zhao, Choueiri, IMVigor210, IMmotion150, Miao, Liu
Wrote cohort access manifest: /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/downloads/cohort_access_manifest.json
Public metadata fetched for 11 cohorts
Public cohort artifacts downloaded: 11/19
Controlled/registration cohorts requiring action: 0
Staged Zenodo deposit inputs for no cohorts
Wrote 0 mapped paired-end FASTQ tasks to /share/lab_goecks/paulo/federated-learning-model/compass_foundation_model_test/public_preprocessing/manifests/public_all16_e13_20261125_020600Z.fastq_runs.tsv
FASTQ preprocessing: not required
Build public ITRP:   22457724
Prepare model data:  22457725
Submit public LOCO:  22457726
Public run tag:      public_all16_e13_20261125_020600Z
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ conda create -n compass-e13-r --override-channels -c conda-forge 'r-base>=4.3' &&
>   rx_rscript=$(conda run -n compass-e13-r which Rscript) &&
>   export COMPASS_RSCRIPT="$rx_rscript"
Retrieving notices: ...working... done
Channels:
 - conda-forge
Platform: linux-64
Collecting package metadata (repodata.json): done
Solving environment: done


==> WARNING: A newer version of conda exists. <==
    current version: 24.1.2
    latest version: 26.10.0

Please update conda by running

    $ conda update -n base -c conda-forge conda



## Package Plan ##

  environment location: /home/4475918/.conda/envs/compass-e13-r

  added / updated specs:
    - r-base[version='>=4.3']


The following packages will be downloaded:

    package                    |            build
    ---------------------------|-----------------
    binutils_impl_linux-64-2.46.1|default_hfdba357_103         3.5 MB  conda-forge
    bwidget-1.10.1             |       hfc2019e_3         131 KB  conda-forge
    c-ares-1.34.9              |       hebe6cf0_0         228 KB  conda-forge
    ca-certificates-2026.11.20 |       hbd8a1cb_0         121 KB  conda-forge
    cairo-1.18.6               |       h3c89d7e_0         984 KB  conda-forge
    curl-8.23.0                |       ha042cf0_0         193 KB  conda-forge
    font-ttf-ubuntu-0.83       |       h77eed37_4         1.5 MB  conda-forge
    fontconfig-2.18.4          |       h4db4eae_0         291 KB  conda-forge
    fribidi-1.0.18             |       h7cc23a3_0          63 KB  conda-forge
    gcc_impl_linux-64-16.2.0   |       h9891192_7        82.1 MB  conda-forge
    gfortran_impl_linux-64-16.2.0|       hf930d89_7        20.2 MB  conda-forge
    gsl-2.8                    |       h3cd6761_2         2.4 MB  conda-forge
    gxx_impl_linux-64-16.2.0   |       h0d273dc_7        16.2 MB  conda-forge
    ld_impl_linux-64-2.46.1    |default_hbd61a6d_103         725 KB  conda-forge
    lerc-4.3.0                 |       he78707d_0         264 KB  conda-forge
    libblas-3.11.0             |12_h4a7cf45_openblas          18 KB  conda-forge
    libcblas-3.11.0            |12_h0358290_openblas          18 KB  conda-forge
    libcurl-8.23.0             |       ha042cf0_0         494 KB  conda-forge
    libdeflate-1.26            |       h351257e_0          73 KB  conda-forge
    libedit-3.1.20260512       | pl5321h373387f_0         133 KB  conda-forge
    libexpat-2.9.0             |       hd2095e1_0          77 KB  conda-forge
    libffi-3.7.0               |       h81df57d_1          66 KB  conda-forge
    libgcc-16.2.0              |       ha9f2e26_7         1.0 MB  conda-forge
    libgcc-devel_linux-64-16.2.0|     he3ce08f_107         3.0 MB  conda-forge
    libgfortran-16.2.0         |       h69a702a_7          28 KB  conda-forge
    libgfortran5-16.2.0        |       h6b99dfc_7         2.4 MB  conda-forge
    libglib-2.90.1             |       hb382ddc_4         4.6 MB  conda-forge
    libgomp-16.2.0             |       he0feb66_7         626 KB  conda-forge
    libharfbuzz-15.0.0         |       h23af247_0         1.6 MB  conda-forge
    libjpeg-turbo-3.2.1        |       h7cc23a3_0         639 KB  conda-forge
    liblapack-3.11.0           |12_h47877c9_openblas          18 KB  conda-forge
    libnghttp2-1.71.0          |       hc5e5977_0         803 KB  conda-forge
    libopenblas-0.3.34         |pthreads_hf13c14d_2         6.5 MB  conda-forge
    libpango-1.58.2            |       hce4e988_3         335 KB  conda-forge
    libpng-1.6.59              |       h922cc85_0         309 KB  conda-forge
    libsanitizer-16.2.0        |       h3048135_7         7.7 MB  conda-forge
    libstdcxx-16.2.0           |       h934c35e_7         6.3 MB  conda-forge
    libstdcxx-devel_linux-64-16.2.0|     h86e191b_107        22.2 MB  conda-forge
    libtiff-4.7.2              |       h6d37cbf_2         449 KB  conda-forge
    libuuid-2.42.4             |       hcfc3c73_1          35 KB  conda-forge
    libxcb-1.17.0              |       hb83e432_3         390 KB  conda-forge
    make-4.4.1                 |       h1114479_4         540 KB  conda-forge
    openssl-3.6.5              |       h781a0a9_0         3.0 MB  conda-forge
    pcre2-10.49                |       h8b3dc9c_0         1.2 MB  conda-forge
    pthread-stubs-0.4          |    h7cc23a3_1004           9 KB  conda-forge
    r-base-4.6.2               |       hc453583_3        27.0 MB  conda-forge
    sed-4.10                   |       h529d415_1         263 KB  conda-forge
    tktable-2.10               |      h0eb2ad0_11         101 KB  conda-forge
    tzdata-2026e               |       h5d301ff_0         116 KB  conda-forge
    xorg-libx11-1.8.14         |       hb83e432_0         827 KB  conda-forge
    xorg-libxau-1.0.12         |       h7cc23a3_2          18 KB  conda-forge
    xorg-libxdmcp-1.1.5        |       h7cc23a3_2          22 KB  conda-forge
    xorg-libxrender-0.9.13     |       h7cc23a3_0          34 KB  conda-forge
    ------------------------------------------------------------
                                           Total:       221.7 MB

The following NEW packages will be INSTALLED:

  _openmp_mutex      conda-forge/linux-64::_openmp_mutex-4.5-20_gnu
  _r-mutex           conda-forge/noarch::_r-mutex-1.0.1-anacondar_1
  binutils_impl_lin~ conda-forge/linux-64::binutils_impl_linux-64-2.46.1-default_hfdba357_103
  bwidget            conda-forge/linux-64::bwidget-1.10.1-hfc2019e_3
  bzip2              conda-forge/linux-64::bzip2-1.0.8-hda65f42_10
  c-ares             conda-forge/linux-64::c-ares-1.34.9-hebe6cf0_0
  ca-certificates    conda-forge/noarch::ca-certificates-2026.11.20-hbd8a1cb_0
  cairo              conda-forge/linux-64::cairo-1.18.6-h3c89d7e_0
  curl               conda-forge/linux-64::curl-8.23.0-ha042cf0_0
  font-ttf-dejavu-s~ conda-forge/noarch::font-ttf-dejavu-sans-mono-2.37-hab24e00_0
  font-ttf-inconsol~ conda-forge/noarch::font-ttf-inconsolata-3.000-h77eed37_0
  font-ttf-source-c~ conda-forge/noarch::font-ttf-source-code-pro-2.038-h77eed37_0
  font-ttf-ubuntu    conda-forge/noarch::font-ttf-ubuntu-0.83-h77eed37_4
  fontconfig         conda-forge/linux-64::fontconfig-2.18.4-h4db4eae_0
  fonts-conda-ecosy~ conda-forge/noarch::fonts-conda-ecosystem-1-0
  fonts-conda-forge  conda-forge/noarch::fonts-conda-forge-1-hc364b38_1
  fribidi            conda-forge/linux-64::fribidi-1.0.18-h7cc23a3_0
  gcc_impl_linux-64  conda-forge/linux-64::gcc_impl_linux-64-16.2.0-h9891192_7
  gfortran_impl_lin~ conda-forge/linux-64::gfortran_impl_linux-64-16.2.0-hf930d89_7
  graphite2          conda-forge/linux-64::graphite2-1.3.15-h54a6638_1
  gsl                conda-forge/linux-64::gsl-2.8-h3cd6761_2
  gxx_impl_linux-64  conda-forge/linux-64::gxx_impl_linux-64-16.2.0-h0d273dc_7
  icu                conda-forge/linux-64::icu-78.3-py310h44b86e0_2
  kernel-headers_li~ conda-forge/noarch::kernel-headers_linux-64-4.18.0-he073ed8_9
  keyutils           conda-forge/linux-64::keyutils-1.6.3-h7cc23a3_1
  krb5               conda-forge/linux-64::krb5-1.22.2-hbc21106_2
  ld_impl_linux-64   conda-forge/linux-64::ld_impl_linux-64-2.46.1-default_hbd61a6d_103
  lerc               conda-forge/linux-64::lerc-4.3.0-he78707d_0
  libblas            conda-forge/linux-64::libblas-3.11.0-12_h4a7cf45_openblas
  libcblas           conda-forge/linux-64::libcblas-3.11.0-12_h0358290_openblas
  libcurl            conda-forge/linux-64::libcurl-8.23.0-ha042cf0_0
  libdeflate         conda-forge/linux-64::libdeflate-1.26-h351257e_0
  libedit            conda-forge/linux-64::libedit-3.1.20260512-pl5321h373387f_0
  libev              conda-forge/linux-64::libev-4.33-h280c20c_3
  libexpat           conda-forge/linux-64::libexpat-2.9.0-hd2095e1_0
  libffi             conda-forge/linux-64::libffi-3.7.0-h81df57d_1
  libfreetype        conda-forge/linux-64::libfreetype-2.14.3-ha770c72_2
  libfreetype6       conda-forge/linux-64::libfreetype6-2.14.3-h5e6c136_2
  libgcc             conda-forge/linux-64::libgcc-16.2.0-ha9f2e26_7
  libgcc-devel_linu~ conda-forge/noarch::libgcc-devel_linux-64-16.2.0-he3ce08f_107
  libgfortran        conda-forge/linux-64::libgfortran-16.2.0-h69a702a_7
  libgfortran5       conda-forge/linux-64::libgfortran5-16.2.0-h6b99dfc_7
  libglib            conda-forge/linux-64::libglib-2.90.1-hb382ddc_4
  libgomp            conda-forge/linux-64::libgomp-16.2.0-he0feb66_7
  libharfbuzz        conda-forge/linux-64::libharfbuzz-15.0.0-h23af247_0
  libiconv           conda-forge/linux-64::libiconv-1.18-h0cb94f2_3
  libjpeg-turbo      conda-forge/linux-64::libjpeg-turbo-3.2.1-h7cc23a3_0
  liblapack          conda-forge/linux-64::liblapack-3.11.0-12_h47877c9_openblas
  liblzma            conda-forge/linux-64::liblzma-5.8.3-hb03c661_1
  libnghttp2         conda-forge/linux-64::libnghttp2-1.71.0-hc5e5977_0
  libopenblas        conda-forge/linux-64::libopenblas-0.3.34-pthreads_hf13c14d_2
  libpango           conda-forge/linux-64::libpango-1.58.2-hce4e988_3
  libpng             conda-forge/linux-64::libpng-1.6.59-h922cc85_0
  libpsl             conda-forge/linux-64::libpsl-0.23.1-hd9e3e90_1
  libsanitizer       conda-forge/linux-64::libsanitizer-16.2.0-h3048135_7
  libssh2            conda-forge/linux-64::libssh2-1.11.1-h6154650_1
  libstdcxx          conda-forge/linux-64::libstdcxx-16.2.0-h934c35e_7
  libstdcxx-devel_l~ conda-forge/noarch::libstdcxx-devel_linux-64-16.2.0-h86e191b_107
  libtiff            conda-forge/linux-64::libtiff-4.7.2-h6d37cbf_2
  libuuid            conda-forge/linux-64::libuuid-2.42.4-hcfc3c73_1
  libwebp-base       conda-forge/linux-64::libwebp-base-1.6.0-hd42ef1d_1
  libxcb             conda-forge/linux-64::libxcb-1.17.0-hb83e432_3
  libzlib            conda-forge/linux-64::libzlib-1.3.2-h25fd6f3_3
  make               conda-forge/linux-64::make-4.4.1-h1114479_4
  ncurses            conda-forge/linux-64::ncurses-6.6-hdb14827_1
  openssl            conda-forge/linux-64::openssl-3.6.5-h781a0a9_0
  pcre2              conda-forge/linux-64::pcre2-10.49-h8b3dc9c_0
  pixman             conda-forge/linux-64::pixman-0.46.4-h54a6638_3
  pthread-stubs      conda-forge/linux-64::pthread-stubs-0.4-h7cc23a3_1004
  r-base             conda-forge/linux-64::r-base-4.6.2-hc453583_3
  readline           conda-forge/linux-64::readline-8.3-hd6e31c0_1
  sed                conda-forge/linux-64::sed-4.10-h529d415_1
  sysroot_linux-64   conda-forge/noarch::sysroot_linux-64-2.28-h4ee821c_9
  tk                 conda-forge/linux-64::tk-8.6.13-noxft_h1df4ec4_4
  tktable            conda-forge/linux-64::tktable-2.10-h0eb2ad0_11
  tzdata             conda-forge/noarch::tzdata-2026e-h5d301ff_0
  xorg-libice        conda-forge/linux-64::xorg-libice-1.1.2-h280c20c_0
  xorg-libsm         conda-forge/linux-64::xorg-libsm-1.2.6-h0d788c3_1
  xorg-libx11        conda-forge/linux-64::xorg-libx11-1.8.14-hb83e432_0
  xorg-libxau        conda-forge/linux-64::xorg-libxau-1.0.12-h7cc23a3_2
  xorg-libxdmcp      conda-forge/linux-64::xorg-libxdmcp-1.1.5-h7cc23a3_2
  xorg-libxext       conda-forge/linux-64::xorg-libxext-1.3.7-h7cc23a3_1
  xorg-libxrender    conda-forge/linux-64::xorg-libxrender-0.9.13-h7cc23a3_0
  xorg-libxt         conda-forge/linux-64::xorg-libxt-1.3.1-h7cc23a3_1
  zstd               conda-forge/linux-64::zstd-1.5.7-hb78ec9c_7


Proceed ([y]/n)? y


Downloading and Extracting Packages:

Preparing transaction: done
Verifying transaction: done
Executing transaction: done
#
# To activate this environment, use
#
#     $ conda activate compass-e13-r
#
# To deactivate an active environment, use
#
#     $ conda deactivate

(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$ qstat
             JOBID PART         NAME     USER ST       TIME  TIME_LEFT NOD CPU TRES_PER_ MIN_ NODELIST(REASON)
          22457725  red prepare_publ  4475918 PD       0:00   12:00:00   1   8       N/A  64G (DependencyNeverSatisfied)
          22457726  red submit_publi  4475918 PD       0:00      30:00   1   1       N/A   2G (Dependency)
(compass-foundation-test) 4475918@hpctpa3pl0001:federated-learning-model(main *)$
