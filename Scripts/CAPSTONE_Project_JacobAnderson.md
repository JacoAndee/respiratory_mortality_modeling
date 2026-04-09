# Bayesian Spatiotemporal Analysis of Ozone Pollution in California

**Author: Jacob Anderson**

**Mentor: Orhun Aydin**

**Research Question**: To what extent does tropospheric ozone exposure
explain spatial variation in respiratory mortality across the state of
California, and which Bayesian spatial modeling framework — Gaussian
BYM2 or Poisson BYM2 — accurately captures this relationship while
quantifying uncertainty and identifying high-risk communities?

**The problem**: Respiratory mortality varies substantially across
California, and tropospheric ozone—driven by meteorology, emissions, and
land use coverage is a major contributor to elevated ozone
concentrations. However, accurately quantifying the relationship between
ozone exposure and respiratory health remains challenging because both
ozone and mortality exhibit strong spatial autocorrelation, measurement
uncertainty, and heterogeneity across counties. Remotely sensed ozone
estimates introduce additional uncertainty due to unit conversion
assumptions and vertical column effects, while traditional regression
models cannot properly account for spatial dependence or unequal
population structures across counties. As a result, existing approaches
risk producing biased effect estimates and misleading conclusions about
which communities face the greatest ozone related health risk. A spatial
Bayesian framework is needed to appropriately model these uncertainties,
capture geographic patterns in exposure and mortality, and provide
reliable inference for public health decision making in the state of
California.

### Preliminary Tasks: Load libraries, set directories, and credentials

    ### Load packages into R environment

    library(arcgisbinding)

    ## *** Please call arc.check_product() to define a desktop license.

    library(raster)

    ## Warning: package 'raster' was built under R version 4.4.3

    ## Loading required package: sp

    ## Warning: package 'sp' was built under R version 4.4.2

    library(sf)

    ## Warning: package 'sf' was built under R version 4.4.3

    ## Linking to GEOS 3.13.0, GDAL 3.10.1, PROJ 9.5.1; sf_use_s2() is TRUE

    library(spdep)

    ## Loading required package: spData

    ## To access larger datasets in this package, install the spDataLarge
    ## package with: `install.packages('spDataLarge',
    ## repos='https://nowosad.github.io/drat/', type='source')`

    library(dplyr)

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:raster':
    ## 
    ##     intersect, select, union

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

    library(corrplot)

    ## Warning: package 'corrplot' was built under R version 4.4.3

    ## corrplot 0.95 loaded

    library(performance)

    ## Warning: package 'performance' was built under R version 4.4.3

    library(Matrix)

    ## Warning: package 'Matrix' was built under R version 4.4.3

    library(car)

    ## Warning: package 'car' was built under R version 4.4.3

    ## Loading required package: carData

    ## Warning: package 'carData' was built under R version 4.4.3

    ## 
    ## Attaching package: 'car'

    ## The following object is masked from 'package:dplyr':
    ## 
    ##     recode

    library(INLA)

    ## Warning: package 'INLA' was built under R version 4.4.2

    ## This is INLA_24.12.11 built 2024-12-11 19:58:26 UTC.
    ##  - See www.r-inla.org/contact-us for how to get help.
    ##  - List available models/likelihoods/etc with inla.list.models()
    ##  - Use inla.doc(<NAME>) to access documentation

    library(bayesplot)

    ## Warning: package 'bayesplot' was built under R version 4.4.3

    ## This is bayesplot version 1.12.0

    ## - Online documentation and vignettes at mc-stan.org/bayesplot

    ## - bayesplot theme set to bayesplot::theme_default()

    ##    * Does _not_ affect other ggplot2 plots

    ##    * See ?bayesplot_theme_set for details on theme setting

    library(ggplot2)

    ## Warning: package 'ggplot2' was built under R version 4.4.3

    library(viridis)

    ## Loading required package: viridisLite

    library(RColorBrewer)

    arc.check_product()

    ## product: ArcGIS Pro (13.5.0.57366)
    ## license: Advanced
    ## version: 1.0.1.311

    arc.check_portal()

    ## *** Current
    ##   url        : https://gisanddata.maps.arcgis.com/
    ##   version    : 2026.1
    ##   user       : jande212_GISandData
    ##   organization   : ArcGIS Online at Johns Hopkins University
    ## *** Available (signed in)
    ##   'https://www.arcgis.com/'
    ## *** Not signed in
    ##   'https://jacob-anderson16.maps.arcgis.com/'

    ### Important directories for project

    ### Set the working directory for the project

    setwd("C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data")

    ### Set data directory as R object

    data_dir <- "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data"

    ### Set geodatabase directory as R object

    gdb <- "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/Project_Data.gdb"

    ### arc.open function to open the main data frame

    fc <- arc.open(file.path(data_dir, "Project_Data.gdb/model_df"))

    ### arc.select to select the data frame

    fc_df <- arc.select(fc)

    ### arc.data2sf to convert ArcGIS data to sf object

    fc_df <- arc.data2sf(fc_df)

### Preliminary Tasks: Calculate rates and log offset for Bayesian Spatial Regression

    ### Calculate total mortality rate
    ### Calculate respiratory mortality rate

    fc_df <- st_transform(fc_df, 3310) %>%
      mutate(
        mortality_rate = (All_Mortality / TOT_POP) * 1e5,
        resp_mortality_rate = (RespiratoryDeaths / TOT_POP) * 1e5,
        resp_deaths = RespiratoryDeaths,
        log_pop = log(TOT_POP))

    ### Drop non essential columns

    fc_df <- fc_df %>% 
      select(where(~ !all(is.na(.))))

### Raster data: NASA TEMPO Ozone for 2024 (Converted from DU to ppm)

    ### Read ozone rasters (ppm) and plot for each month in 2024

    month_names <- paste0("o3_", ifelse(1:12 < 10, paste0("0", 1:12), 1:12))

    ### Apply 3x4 grid to plot

    par(mfrow = c(3, 4), mar = c(2, 2, 2, 5))

    ### Loop to display the raster data

    for (m in month_names) {
      ras_path <- file.path(gdb, m)
      ras <- arc.open(ras_path)
      ras_o3 <- arc.raster(ras)
      o3_data <- as.raster(ras_o3)
      plot(o3_data, main = toupper(m))
    }

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Display%20raster%20values-1.png)

### Exploratory analysis of key variables - Part 1

    ### Histogram for target variable (rate)

    hist(fc_df$resp_mortality_rate,
         breaks = 18,
         col = "grey",
         border = "black",
         main = "Distribution of Respiratory Related Mortality",
         xlab = "Number of Deaths from Respiratory Illness",
         ylab = "Frequency")

    ### Add the mean line

    abline(v = mean(fc_df$resp_mortality_rate,
                    na.rm = T),
           col = "red",
           lwd = 2,
           lty = 2)

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Exploratory%20Data%20Analysis%20Part%201%20-%20Histogram-1.png)

### Exploratory analysis of key variables - Part 2

    ### Box plots for mean and max ozone for each month

    mean_cols <- paste0("MEAN_o3_", ifelse(1:12 < 10, paste0("0", 1:12), 1:12))

    max_cols <- paste0("MAX_o3_", ifelse(1:12 < 10, paste0("0", 1:12), 1:12))

    ### Prepare plot area

    par(mfrow = c(1, 1), mar = c(6, 5, 4, 2))

    ### Collect the columns for each month
    ### Store in list

    plot_data <- list()
    plot_labels <- character(0)

    ### Plot the mean ozone concentrations

    mean_data <- vector("list", 12)
    for (i in 1:12) {
      mean_data[[i]] <- as.numeric(fc_df[[mean_cols[i]]])
    }
    par(mar = c(6, 5, 4, 2))
    boxplot(mean_data,
            names = month.abb,
            las = 2,
            col = "grey",
            outline = T, 
            pch = 19, 
            cex = 0.6, 
            boxwex = 0.6,
            ylab = "Ozone (ppm)",
            main = "Monthly Ozone — MEAN")

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Exploratory%20Data%20Analysis%20Part%202%20-%20Box%20Plots-1.png)

    ### Plot the max ozone concentrations

    max_data <- vector("list", 12)
    for (i in 1:12) {
      max_data[[i]] <- as.numeric(fc_df[[max_cols[i]]])
    }
    par(mar = c(6, 5, 4, 2))
    boxplot(max_data,
            names = month.abb,
            las = 2,
            col = "grey",
            outline = T, 
            pch = 19, 
            cex = 0.6, 
            boxwex = 0.6,
            ylab = "Ozone (ppm)",
            main = "Monthly Ozone — MAX")

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Exploratory%20Data%20Analysis%20Part%202%20-%20Box%20Plots-2.png)

### Test for Spatial Autocorrelation

    ### Test for spatial autocorrelation

    ### Build neighbors & weights

    nb <- poly2nb(as_Spatial(fc_df))
    lw <- nb2listw(nb, style = "W", zero.policy = T)

    ### Global Moran's I: respiratory mortality rate

    print("Global Moran's I: Respiratory mortality rate")

    ## [1] "Global Moran's I: Respiratory mortality rate"

    g_morans_resp <- moran.test(fc_df$resp_mortality_rate, lw, zero.policy = T)

    g_morans_resp_results <- data.frame(
      variable = "resp_mortality_rate",
      morans_I = unname(g_morans_resp$estimate[["Moran I statistic"]]),
      expectation = unname(g_morans_resp$estimate[["Expectation"]]),
      variance = unname(g_morans_resp$estimate[["Variance"]]),
      p_value = g_morans_resp$p.value
    )

    ### Write the results to table

    g_morans_resp_results <- write.csv(g_morans_resp_results, file.path(data_dir, "respiratory_morans.csv"), row.names = F)

    ### Ozone column names

    mean_cols <- paste0("MEAN_o3_", ifelse(1:12 < 10, paste0("0", 1:12), 1:12))
    max_cols <- paste0("MAX_o3_", ifelse(1:12 < 10, paste0("0", 1:12), 1:12))


    ### Global Moran's I ozone concentrations (Mean & Max by month)

    mi_vals_mean <- numeric(12) 
    p_vals_mean <- numeric(12)
    mi_vals_max <- numeric(12)
    p_vals_max <- numeric(12)

    print("Global Moran's I: Ozone (monthly MEAN)")

    ## [1] "Global Moran's I: Ozone (monthly MEAN)"

    for (i in 1:12) {
      v_mean <- as.numeric(fc_df[[mean_cols[i]]])
      mi_mean <- moran.test(v_mean, lw, zero.policy = T)
      mi_vals_mean[i] <- unname(mi_mean$estimate[["Moran I statistic"]])
      p_vals_mean[i] <- mi_mean$p.value
      print(mi_mean)
    }

    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 9.2405, p-value < 2.2e-16
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.747172721      -0.017543860       0.006848792 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 6.7361, p-value = 8.134e-12
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.527803400      -0.017543860       0.006554324 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 6.2834, p-value = 1.656e-10
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.499104452      -0.017543860       0.006760885 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 7.9088, p-value = 1.3e-15
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.624892720      -0.017543860       0.006598455 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 5.8281, p-value = 2.804e-09
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.465715416      -0.017543860       0.006875598 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 4.6672, p-value = 1.527e-06
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.358322638      -0.017543860       0.006485638 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 5.2835, p-value = 6.336e-08
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.423883973      -0.017543860       0.006980236 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 7.4148, p-value = 6.092e-14
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.603951964      -0.017543860       0.007025583 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 3.5022, p-value = 0.0002308
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.275592044      -0.017543860       0.007005961 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 5.68, p-value = 6.734e-09
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.458327768      -0.017543860       0.007019109 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 8.1337, p-value < 2.2e-16
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.660214671      -0.017543860       0.006943436 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_mean  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 10.458, p-value < 2.2e-16
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.863285206      -0.017543860       0.007094056

    print("Global Moran's I: Ozone (monthly MAX)")

    ## [1] "Global Moran's I: Ozone (monthly MAX)"

    for (i in 1:12) {
      v_max <- as.numeric(fc_df[[max_cols[i]]])
      mi_max <- moran.test(v_max, lw, zero.policy = T)
      mi_vals_max[i] <- unname(mi_max$estimate[["Moran I statistic"]])
      p_vals_max[i]  <- mi_max$p.value
      print(mi_max)
    }

    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 6.0935, p-value = 5.524e-10
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.492172032      -0.017543860       0.006997206 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 6.9866, p-value = 1.408e-12
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.560507974      -0.017543860       0.006845442 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 6.1711, p-value = 3.391e-10
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##        0.49716157       -0.01754386        0.00695655 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 6.2158, p-value = 2.553e-10
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.481228777      -0.017543860       0.006438843 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 7.1874, p-value = 3.302e-13
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.571125284      -0.017543860       0.006708111 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 4.9703, p-value = 3.343e-07
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.216395935      -0.017543860       0.002215359 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 4.5473, p-value = 2.717e-06
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.355727972      -0.017543860       0.006738305 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 4.5066, p-value = 3.294e-06
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.356227323      -0.017543860       0.006878784 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 2.7276, p-value = 0.00319
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.189370349      -0.017543860       0.005754697 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 5.5527, p-value = 1.406e-08
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.378111157      -0.017543860       0.005077202 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 4.769, p-value = 9.255e-07
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.371736848      -0.017543860       0.006662913 
    ## 
    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  v_max  
    ## weights: lw    
    ## 
    ## Moran I statistic standard deviate = 5.3554, p-value = 4.269e-08
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##        0.42326762       -0.01754386        0.00677525

    o3_morans_results <- data.frame(
      month = 1:12,
      label = month.abb,
      morans_I_mean = mi_vals_mean,
      p_mean = p_vals_mean,
      morans_I_max = mi_vals_max,
      p_max = p_vals_max
    )

    ### Write the results to table

    o3_morans_results <- write.csv(o3_morans_results, file.path(data_dir, "o3_morans.csv"), row.names = F)

    ### Local Gi*: Respiratory mortality rate

    gi_resp <- localG(fc_df$resp_mortality_rate, lw, zero.policy = T)
    fc_df$gi_resp <- as.numeric(gi_resp)

    ### Local Gi*: Ozone (Mean & Max by month)

    for (i in 1:12) {
      gi_mean <- localG(as.numeric(fc_df[[mean_cols[i]]]), lw, zero.policy = T)
      gi_max <- localG(as.numeric(fc_df[[max_cols[i]]]),  lw, zero.policy = T)
      fc_df[[paste0("gi_", mean_cols[i])]] <- as.numeric(gi_mean)
      fc_df[[paste0("gi_", max_cols[i])]] <- as.numeric(gi_max)
    }

    ### Gi* class settings

    gi_breaks <- c(-Inf, -2.58, -1.96, 1.96, 2.58, Inf)
    gi_labs <- c("Cold (99%)","Cold (95%)","Not Sig","Hot (95%)","Hot (99%)")
    pal_vals <- c("#084594", "#4292c6", "grey90", "#fb6a4a", "#cb181d"); names(pal_vals) <- gi_labs

    ### Respiratory mortality Gi* plot

    op <- par(no.readonly = T)
    par(mar = c(1,1,3,1))
    fc_df$gi_class_resp <- cut(fc_df$gi_resp, breaks = gi_breaks, labels = gi_labs)
    cols_resp <- pal_vals[as.character(fc_df$gi_class_resp)]
    plot(st_geometry(fc_df), 
         col = cols_resp, 
         border = "grey", 
         lwd = 0.01,
         main = "Gi* — Respiratory Death Rate")
    legend("bottomleft", fill = pal_vals, legend = names(pal_vals), bty = "n", cex = 0.9)

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Spatial%20Autocorrelation-1.png)

    ### Build matrices of monthly Gi* z-scores for plot

    gi_mean_mat <- cbind(
      as.numeric(fc_df[["gi_MEAN_o3_01"]]), as.numeric(fc_df[["gi_MEAN_o3_02"]]),
      as.numeric(fc_df[["gi_MEAN_o3_03"]]), as.numeric(fc_df[["gi_MEAN_o3_04"]]),
      as.numeric(fc_df[["gi_MEAN_o3_05"]]), as.numeric(fc_df[["gi_MEAN_o3_06"]]),
      as.numeric(fc_df[["gi_MEAN_o3_07"]]), as.numeric(fc_df[["gi_MEAN_o3_08"]]),
      as.numeric(fc_df[["gi_MEAN_o3_09"]]), as.numeric(fc_df[["gi_MEAN_o3_10"]]),
      as.numeric(fc_df[["gi_MEAN_o3_11"]]), as.numeric(fc_df[["gi_MEAN_o3_12"]])
    )

    gi_max_mat <- cbind(
      as.numeric(fc_df[["gi_MAX_o3_01"]]), as.numeric(fc_df[["gi_MAX_o3_02"]]),
      as.numeric(fc_df[["gi_MAX_o3_03"]]), as.numeric(fc_df[["gi_MAX_o3_04"]]),
      as.numeric(fc_df[["gi_MAX_o3_05"]]), as.numeric(fc_df[["gi_MAX_o3_06"]]),
      as.numeric(fc_df[["gi_MAX_o3_07"]]), as.numeric(fc_df[["gi_MAX_o3_08"]]),
      as.numeric(fc_df[["gi_MAX_o3_09"]]), as.numeric(fc_df[["gi_MAX_o3_10"]]),
      as.numeric(fc_df[["gi_MAX_o3_11"]]), as.numeric(fc_df[["gi_MAX_o3_12"]])
    )

    ### 3×4 Gi* plot: Ozone MEAN

    layout(matrix(c( 1,  2,  3,  4, 13,
                     5,  6,  7,  8, 13,
                     9, 10, 11, 12, 13), nrow = 3, byrow = T),
           widths = c(1,1,1,1,0.50), heights = c(1,1,1))

    par(mar = c(1,1,3,1))

    for (i in 1:12) {
      cl <- cut(gi_mean_mat[, i], breaks = gi_breaks, labels = gi_labs)
      cols <- pal_vals[as.character(cl)]
      plot(st_geometry(fc_df), col = cols, border = "grey", lwd = 0.01,
           main = paste0("Gi* Ozone Mean — ", month.abb[i]))
    }

    par(mar = c(0,0,0,0)); plot.new()

    legend("center", fill = pal_vals, legend = names(pal_vals), ncol = 1, bty = "n", cex = 1)

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Spatial%20Autocorrelation-2.png)

    layout(1)

    ### 3×4 Gi* plot: Ozone MAX

    layout(matrix(c( 1,  2,  3,  4, 13,
                     5,  6,  7,  8, 13,
                     9, 10, 11, 12, 13), nrow = 3, byrow = T),
           widths = c(1,1,1,1,0.50), heights = c(1,1,1))

    par(mar = c(1,1,3,1))

    for (i in 1:12) {
      cl   <- cut(gi_max_mat[, i], breaks = gi_breaks, labels = gi_labs)
      cols <- pal_vals[as.character(cl)]
      plot(st_geometry(fc_df), col = cols, border = "grey", lwd = 0.01,
           main = paste0("Gi* Ozone Max — ", month.abb[i]))
    }

    par(mar = c(0,0,0,0)); plot.new()

    legend("center", fill = pal_vals, legend = names(pal_vals), ncol = 1, bty = "n", cex = 1)

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Spatial%20Autocorrelation-3.png)

    layout(1)

    par(op)

### Data management: Aggregate for annual ozone concentrations

    ### Aggregate all ozone measurements (mean & max) to annual estimates for each county

    fc_no_geom <- st_drop_geometry(fc_df)

    mean_cols <- paste0("MEAN_o3_", ifelse(1:12 < 10, paste0("0", 1:12), 1:12))

    max_cols <- paste0("MAX_o3_", ifelse(1:12 < 10, paste0("0", 1:12), 1:12))

    fc_no_geom$o3_mean_annual <- rowMeans(fc_no_geom[, mean_cols, drop = F], na.rm = T)

    fc_no_geom$o3_max_annual <- do.call(pmax, c(fc_no_geom[, max_cols], na.rm = T))

### Collinearity diagnostics on the key variables

    ### Collinearity test between covariates

    ### Group land cover variables

    fc_no_geom <- fc_no_geom %>%
      mutate(
        LC_urban = PCT_DEV_OPEN + PCT_DEV_LOW + PCT_DEV_MED + PCT_DEV_HIGH,
        LC_forest = PCT_DEC_FOR + PCT_EVG_FOR + PCT_MX_FOR,
        LC_ag = PCT_CROPLAND + PCT_PASTURE,
        LC_natural = PCT_SHRUB + PCT_GRASSLAND + PCT_BARREN,
        LC_wetlands = PCT_W_WETLAND + PCT_E_WETLAND
      )

    ### Build a list of the variables

    l <- c(
      "LC_urban",
      "LC_forest",
      "LC_ag",
      "LC_natural",
      "LC_wetlands",
      "abnormal_D0",
      "moderate_D1",
      "severe_D2",
      "extreme_D3",
      "MEAN_precip",
      "MEAN_temp",
      "o3_mean_annual",
      "o3_max_annual",
      "PCT_POP_POV",
      "PCT_COM_OVER_90",
      "PCT_POP_DEP_AGE_18_65",
      "PCT_POP_NO_INSUR",
      "resp_mortality_rate"
    )

    cor_vars <- fc_no_geom[, l, drop = F]

    pwise_matrix <- cor(
      cor_vars,
      use = "pairwise.complete.obs")
      round(pwise_matrix, 2)

    ##                       LC_urban LC_forest LC_ag LC_natural LC_wetlands
    ## LC_urban                  1.00     -0.27 -0.08      -0.41       -0.02
    ## LC_forest                -0.27      1.00 -0.48      -0.33       -0.22
    ## LC_ag                    -0.08     -0.48  1.00      -0.38        0.33
    ## LC_natural               -0.41     -0.33 -0.38       1.00       -0.18
    ## LC_wetlands              -0.02     -0.22  0.33      -0.18        1.00
    ## abnormal_D0               0.27     -0.12  0.19      -0.27        0.09
    ## moderate_D1               0.20     -0.27 -0.19       0.31       -0.10
    ## severe_D2                -0.09     -0.22 -0.05       0.33       -0.12
    ## extreme_D3               -0.09     -0.22 -0.05       0.33       -0.13
    ## MEAN_precip              -0.22      0.76 -0.14      -0.48       -0.07
    ## MEAN_temp                 0.44     -0.52  0.31      -0.10        0.07
    ## o3_mean_annual           -0.21      0.55 -0.39      -0.04        0.06
    ## o3_max_annual            -0.26     -0.03 -0.30       0.54       -0.22
    ## PCT_POP_POV              -0.33     -0.07  0.34       0.02       -0.02
    ## PCT_COM_OVER_90          -0.08      0.00  0.09      -0.03        0.08
    ## PCT_POP_DEP_AGE_18_65    -0.56      0.42 -0.14       0.13       -0.04
    ## PCT_POP_NO_INSUR         -0.36     -0.05  0.06       0.31       -0.01
    ## resp_mortality_rate      -0.22      0.34 -0.14      -0.05       -0.10
    ##                       abnormal_D0 moderate_D1 severe_D2 extreme_D3 MEAN_precip
    ## LC_urban                     0.27        0.20     -0.09      -0.09       -0.22
    ## LC_forest                   -0.12       -0.27     -0.22      -0.22        0.76
    ## LC_ag                        0.19       -0.19     -0.05      -0.05       -0.14
    ## LC_natural                  -0.27        0.31      0.33       0.33       -0.48
    ## LC_wetlands                  0.09       -0.10     -0.12      -0.13       -0.07
    ## abnormal_D0                  1.00       -0.05     -0.16      -0.17        0.10
    ## moderate_D1                 -0.05        1.00      0.57       0.56       -0.47
    ## severe_D2                   -0.16        0.57      1.00       0.98       -0.34
    ## extreme_D3                  -0.17        0.56      0.98       1.00       -0.34
    ## MEAN_precip                  0.10       -0.47     -0.34      -0.34        1.00
    ## MEAN_temp                    0.08        0.11      0.24       0.25       -0.36
    ## o3_mean_annual              -0.11       -0.17     -0.36      -0.38        0.31
    ## o3_max_annual               -0.46        0.13      0.06      -0.01       -0.33
    ## PCT_POP_POV                 -0.22        0.14      0.16       0.16        0.03
    ## PCT_COM_OVER_90              0.18       -0.12      0.04       0.08        0.10
    ## PCT_POP_DEP_AGE_18_65       -0.07       -0.08      0.01      -0.03        0.42
    ## PCT_POP_NO_INSUR            -0.22        0.25      0.09       0.10       -0.18
    ## resp_mortality_rate         -0.17       -0.01     -0.08      -0.11        0.51
    ##                       MEAN_temp o3_mean_annual o3_max_annual PCT_POP_POV
    ## LC_urban                   0.44          -0.21         -0.26       -0.33
    ## LC_forest                 -0.52           0.55         -0.03       -0.07
    ## LC_ag                      0.31          -0.39         -0.30        0.34
    ## LC_natural                -0.10          -0.04          0.54        0.02
    ## LC_wetlands                0.07           0.06         -0.22       -0.02
    ## abnormal_D0                0.08          -0.11         -0.46       -0.22
    ## moderate_D1                0.11          -0.17          0.13        0.14
    ## severe_D2                  0.24          -0.36          0.06        0.16
    ## extreme_D3                 0.25          -0.38         -0.01        0.16
    ## MEAN_precip               -0.36           0.31         -0.33        0.03
    ## MEAN_temp                  1.00          -0.77         -0.26       -0.13
    ## o3_mean_annual            -0.77           1.00          0.29       -0.07
    ## o3_max_annual             -0.26           0.29          1.00        0.05
    ## PCT_POP_POV               -0.13          -0.07          0.05        1.00
    ## PCT_COM_OVER_90           -0.05          -0.08         -0.22       -0.03
    ## PCT_POP_DEP_AGE_18_65     -0.50           0.21          0.12        0.23
    ## PCT_POP_NO_INSUR          -0.24           0.04          0.23        0.44
    ## resp_mortality_rate       -0.19           0.15          0.14        0.15
    ##                       PCT_COM_OVER_90 PCT_POP_DEP_AGE_18_65 PCT_POP_NO_INSUR
    ## LC_urban                        -0.08                 -0.56            -0.36
    ## LC_forest                        0.00                  0.42            -0.05
    ## LC_ag                            0.09                 -0.14             0.06
    ## LC_natural                      -0.03                  0.13             0.31
    ## LC_wetlands                      0.08                 -0.04            -0.01
    ## abnormal_D0                      0.18                 -0.07            -0.22
    ## moderate_D1                     -0.12                 -0.08             0.25
    ## severe_D2                        0.04                  0.01             0.09
    ## extreme_D3                       0.08                 -0.03             0.10
    ## MEAN_precip                      0.10                  0.42            -0.18
    ## MEAN_temp                       -0.05                 -0.50            -0.24
    ## o3_mean_annual                  -0.08                  0.21             0.04
    ## o3_max_annual                   -0.22                  0.12             0.23
    ## PCT_POP_POV                     -0.03                  0.23             0.44
    ## PCT_COM_OVER_90                  1.00                  0.21            -0.01
    ## PCT_POP_DEP_AGE_18_65            0.21                  1.00             0.25
    ## PCT_POP_NO_INSUR                -0.01                  0.25             1.00
    ## resp_mortality_rate             -0.03                  0.43             0.00
    ##                       resp_mortality_rate
    ## LC_urban                            -0.22
    ## LC_forest                            0.34
    ## LC_ag                               -0.14
    ## LC_natural                          -0.05
    ## LC_wetlands                         -0.10
    ## abnormal_D0                         -0.17
    ## moderate_D1                         -0.01
    ## severe_D2                           -0.08
    ## extreme_D3                          -0.11
    ## MEAN_precip                          0.51
    ## MEAN_temp                           -0.19
    ## o3_mean_annual                       0.15
    ## o3_max_annual                        0.14
    ## PCT_POP_POV                          0.15
    ## PCT_COM_OVER_90                     -0.03
    ## PCT_POP_DEP_AGE_18_65                0.43
    ## PCT_POP_NO_INSUR                     0.00
    ## resp_mortality_rate                  1.00

    plot_cols <- colorRampPalette(brewer.pal(11, "RdBu"))(200)

    corrplot(
      pwise_matrix,
      col = plot_cols,
      method = "color",
      type = "full",
      tl.col = "black",
      tl.cex = 0.3,
      order = "hclust",
      addrect = 4,
      mar = c(0, 0, 1, 0)
    )

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Collinearity%20Test-1.png)

    ### Variables used in the VIF test

    vif_vars <- fc_no_geom[, c(
      "LC_urban",
      "LC_forest",
      "LC_ag",
      "LC_natural",
      "LC_wetlands",
      "abnormal_D0",
      "moderate_D1",
      "severe_D2",
      "MEAN_precip",
      "MEAN_temp",
      "o3_mean_annual",
      "PCT_POP_POV",
      "PCT_COM_OVER_90",
      "PCT_POP_DEP_AGE_18_65",
      "PCT_POP_NO_INSUR"
    )]

    ### Fit a simple linear model to compute VIF

    vif_mod <- lm(fc_no_geom$resp_mortality_rate ~ ., data = vif_vars)

    ### Compute VIF

    vif_results <- vif(vif_mod)
    print(vif_results)

    ##              LC_urban             LC_forest                 LC_ag 
    ##            142.297821            234.521654            194.545814 
    ##            LC_natural           LC_wetlands           abnormal_D0 
    ##            246.375230              5.234084              1.401106 
    ##           moderate_D1             severe_D2           MEAN_precip 
    ##              2.435873              2.410083              4.374279 
    ##             MEAN_temp        o3_mean_annual           PCT_POP_POV 
    ##              4.108388              3.987666              1.876332 
    ##       PCT_COM_OVER_90 PCT_POP_DEP_AGE_18_65      PCT_POP_NO_INSUR 
    ##              1.162448              2.177374              1.850878

### Establish the predictors for Bayesian spatial models

    ### Establish the predictors for Gaussian and Poisson models
    ### Setting the target variable as new R object

    resp_var <- "resp_mortality_rate"

    ### Setting the predictor variables as new R obect

    pred_annual <- c(
      "o3_mean_annual",
      "MEAN_temp",
      "MEAN_precip",
      "severe_D2",
      "LC_urban",
      "PCT_POP_POV",
      "PCT_COM_OVER_90",
      "PCT_POP_DEP_AGE_18_65",
      "PCT_POP_NO_INSUR"
    )

    pred_annual <- intersect(pred_annual, names(fc_no_geom))

    for (nm in unique(c(resp_var, pred_annual))) {
      fc_no_geom[[nm]] <- as.numeric(fc_no_geom[[nm]])
    }

### Sampling from the prior distribution

    ### Sample for prior probability distribution

    ### Set seed for reproducibility

    set.seed(123)

    x_raw <- as.matrix(fc_no_geom[, pred_annual, drop = F])

    x_scaled <- scale(x_raw)

    x <- cbind(Intercept = 1, x_scaled)

    y <- as.numeric(fc_no_geom[[resp_var]])

    beta0_mean <- mean(y, na.rm = T)

    beta0_sd <- sd(y, na.rm = T)

    slope_sd <- 5

    sigma_obs <- sd(y, na.rm = T) / 2

    n_draws <- 5000

    p <- ncol(x)

    beta <- matrix(0,
                   nrow = p, 
                   ncol = n_draws)

    beta[1,] <- rnorm(n_draws, beta0_mean, beta0_sd)

    if (p > 1) {
      beta[2:p, ] <- matrix(rnorm((p - 1) * n_draws, 0, slope_sd), nrow = p - 1)
    }

    mu_prior <- x %*% beta

    y_prior <- mu_prior + matrix(rnorm(length(mu_prior), 0, sigma_obs), nrow = nrow(mu_prior))

    ### Plot the prior probability distribution

    df_prior <- data.frame(y = as.numeric(y_prior))
    ggplot(df_prior, aes(x = y)) +
      geom_density(fill = "grey", alpha = 0.5) +
      theme_minimal() +
      labs(
        title = "Prior Distribution (Gaussian)",
        x = "Respiratory Mortality",
        y = "Density"
      )

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Sample%20from%20prior%20distribution-1.png)

### Fit the Gaussian BYM2 Spatial Model

    ### Build spatial adjacency

    nb <- poly2nb(as_Spatial(fc_df))

    a <- nb2mat(nb, style = "B")

    a[is.na(a)] <- 0

    a <- (a + t(a)) > 0

    a <- Matrix(a * 1, sparse = T)

    g <- inla.read.graph(a)

    ### Scale the model

    x_a <- scale(as.matrix(fc_no_geom[, pred_annual, drop = F]))

    colnames(x_a) <- pred_annual

    df_model_annual <- fc_no_geom[, c(resp_var, pred_annual), drop = F]

    for (nm in pred_annual) df_model_annual[[nm]] <- x_a[, nm]

    df_model_annual$idx <- seq_len(nrow(df_model_annual))

    ### Formula (Gaussian BYM2)

    form_a <- resp_mortality_rate ~ 
      o3_mean_annual +
      MEAN_temp +
      MEAN_precip +
      severe_D2 +
      LC_urban +
      PCT_POP_POV +
      PCT_COM_OVER_90 +
      PCT_POP_DEP_AGE_18_65 +
      PCT_POP_NO_INSUR +
      f(idx, 
        model = "bym2",
        graph = g, 
        scale.model = T,
        hyper = list(
          prec = list(prior = "pc.prec", param = c(0.5, 0.5)),
          phi = list(prior = "pc", param = c(0.5, 0.5))
        ))

    ### Model fit (Gaussian BYM2)

    fit_a <- inla(
      formula = form_a,
      data = df_model_annual,
      family = "gaussian",
      control.fixed = list(
        mean.intercept = beta0_mean,
        prec.intercept = 1 / (beta0_sd ^ 2 + 1e-8),
        mean = 0,
        prec = 1 / (slope_sd ^ 2)
      ),
      control.family = list(
        hyper = list(prec = list(prior = "pc.prec", param = c(50, 0.5)))
      ),
      control.compute = list(dic = T, waic = T, cpo = T, return.marginals.predictor = T, config = T)
    )

    summary(fit_a)

    ## Time used:
    ##     Pre = 10.3, Running = 0.381, Post = 0.474, Total = 11.2 
    ## Fixed effects:
    ##                          mean     sd 0.025quant 0.5quant 0.975quant    mode kld
    ## (Intercept)           476.483 25.466    426.479  476.483    526.488 476.483   0
    ## o3_mean_annual          0.945  4.912     -8.688    0.945     10.576   0.945   0
    ## MEAN_temp              -1.207  4.914    -10.842   -1.208      8.428  -1.208   0
    ## MEAN_precip             3.587  4.926     -6.074    3.588     13.244   3.588   0
    ## severe_D2              -0.531  4.910    -10.158   -0.531      9.097  -0.531   0
    ## LC_urban               -1.443  4.913    -11.076   -1.443      8.192  -1.443   0
    ## PCT_POP_POV             1.048  4.911     -8.582    1.049     10.677   1.049   0
    ## PCT_COM_OVER_90        -0.289  4.909     -9.914   -0.289      9.336  -0.289   0
    ## PCT_POP_DEP_AGE_18_65   3.034  4.922     -6.619    3.035     12.684   3.035   0
    ## PCT_POP_NO_INSUR       -0.083  4.910     -9.710   -0.083      9.545  -0.083   0
    ## 
    ## Random effects:
    ##   Name     Model
    ##     idx BYM2 model
    ## 
    ## Model hyperparameters:
    ##                                           mean    sd 0.025quant 0.5quant
    ## Precision for the Gaussian observations  0.000  0.00      0.000    0.000
    ## Precision for idx                       98.150 17.43     74.599   94.903
    ## Phi for idx                              0.079  0.01      0.063    0.078
    ##                                         0.975quant   mode
    ## Precision for the Gaussian observations      0.000  0.000
    ## Precision for idx                          141.513 85.113
    ## Phi for idx                                  0.102  0.074
    ## 
    ## Deviance Information Criterion (DIC) ...............: 779.13
    ## Deviance Information Criterion (DIC, saturated) ....: -193.88
    ## Effective number of parameters .....................: 1.66
    ## 
    ## Watanabe-Akaike information criterion (WAIC) ...: 779.54
    ## Effective number of parameters .................: 1.99
    ## 
    ## Marginal log-Likelihood:  -366.93 
    ## CPO, PIT is computed 
    ## Posterior summaries for the linear predictor and the fitted values are computed
    ## (Posterior marginals needs also 'control.compute=list(return.marginals.predictor=TRUE)')

### Fit the Poisson BYM2 Spatial Model

    ### Build Poisson model data frame

    ### Reuse scaled predictors

    fc_no_geom$resp_deaths <- as.numeric(fc_no_geom$RespiratoryDeaths)
    fc_no_geom$log_pop <- log(fc_no_geom$TOT_POP)

    df_model_pois <- fc_no_geom[, c("resp_deaths", pred_annual, "log_pop"), drop = F]

    for (nm in pred_annual) {
      df_model_pois[[nm]] <- x_a[, nm]
    }

    df_model_pois$idx <- seq_len(nrow(df_model_pois))

    ### Formula (Poisson BYM2)

    form_b <- resp_deaths ~ 
      o3_mean_annual +
      MEAN_temp +
      MEAN_precip +
      severe_D2 +
      LC_urban +
      PCT_POP_POV +
      PCT_COM_OVER_90 +
      PCT_POP_DEP_AGE_18_65 +
      PCT_POP_NO_INSUR +
      f(
        idx,
        model = "bym2",
        graph = g,
        scale.model = T,
        hyper = list(
          prec = list(prior = "pc.prec", param = c(0.5, 0.5)),
          phi = list(prior = "pc", param = c(0.5, 0.5))
        )
      ) +
      offset(log_pop)

    ### Model fit (Poisson BYM2)

    fit_b <- inla(
      formula = form_b,
      data    = df_model_pois,
      family  = "poisson",
      control.fixed = list(
        mean.intercept = 0,
        prec.intercept = 1 / (5^2),
        mean = 0,
        prec = 1 / (slope_sd ^ 2)
      ),
      control.family = list(
        link = "log"
      ),
      control.compute = list(dic = T, waic  = T, cpo = T, return.marginals.predictor = T, config = T
      )
    )

    summary(fit_b)

    ## Time used:
    ##     Pre = 9.81, Running = 0.316, Post = 0.493, Total = 10.6 
    ## Fixed effects:
    ##                         mean    sd 0.025quant 0.5quant 0.975quant   mode kld
    ## (Intercept)           -5.403 0.035     -5.474   -5.403     -5.333 -5.403   0
    ## o3_mean_annual         0.053 0.083     -0.108    0.052      0.220  0.052   0
    ## MEAN_temp              0.111 0.095     -0.069    0.109      0.303  0.109   0
    ## MEAN_precip            0.168 0.074      0.027    0.166      0.322  0.166   0
    ## severe_D2             -0.009 0.056     -0.121   -0.009      0.102 -0.009   0
    ## LC_urban               0.015 0.055     -0.095    0.015      0.124  0.015   0
    ## PCT_POP_POV            0.035 0.049     -0.061    0.035      0.130  0.035   0
    ## PCT_COM_OVER_90        0.001 0.053     -0.101    0.000      0.107  0.000   0
    ## PCT_POP_DEP_AGE_18_65  0.167 0.059      0.051    0.167      0.284  0.167   0
    ## PCT_POP_NO_INSUR      -0.058 0.058     -0.171   -0.058      0.056 -0.058   0
    ## 
    ## Random effects:
    ##   Name     Model
    ##     idx BYM2 model
    ## 
    ## Model hyperparameters:
    ##                     mean    sd 0.025quant 0.5quant 0.975quant  mode
    ## Precision for idx 10.119 2.662      5.863    9.792     16.267 9.174
    ## Phi for idx        0.359 0.208      0.048    0.331      0.799 0.184
    ## 
    ## Deviance Information Criterion (DIC) ...............: 612.80
    ## Deviance Information Criterion (DIC, saturated) ....: 123.05
    ## Effective number of parameters .....................: 55.65
    ## 
    ## Watanabe-Akaike information criterion (WAIC) ...: 599.94
    ## Effective number of parameters .................: 31.01
    ## 
    ## Marginal log-Likelihood:  -414.01 
    ## CPO, PIT is computed 
    ## Posterior summaries for the linear predictor and the fitted values are computed
    ## (Posterior marginals needs also 'control.compute=list(return.marginals.predictor=TRUE)')

### Plot the results from the Gaussian BYM2 Spatial Model

    sf_a <- df_model_annual

    st_geometry(sf_a) <- st_geometry(fc_df)

    st_crs(sf_a) <- st_crs(fc_df)

    ### Model Results

    sum_a <- fit_a$summary.fitted.values
    sf_a$fit_mean <- sum_a$mean
    sf_a$fit_sd <- sum_a$sd
    sf_a$fit_lcl <- sum_a$`0.025quant`
    sf_a$fit_ucl <- sum_a$`0.975quant`
    sf_a$fit_ci <- sf_a$fit_ucl - sf_a$fit_lcl

    ### Map posterior mean, sd, and ci (Gaussian)

    pa_mean <- ggplot(sf_a) +
      geom_sf(aes(fill = fit_mean), color = "grey", linewidth = 0.01) +
      scale_fill_distiller(name = "Posterior Mean", palette = "RdYlBu", direction = -1) +
      labs(title = "Posterior Mean (Gaussian BYM2)") +
      theme_minimal() +
      theme(
        legend.position = "right",
        plot.title = element_text(face = "bold"),
        panel.grid.major = element_line(linewidth = 0.1, linetype = "dotted")
      )
    pa_mean

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Plot%20results%20-%20Gaussian-1.png)

    pa_sd <- ggplot(sf_a) +
      geom_sf(aes(fill = fit_sd), color = "grey", linewidth = 0.01) +
      scale_fill_distiller(name = "Posterior SD", palette = "RdYlBu", direction = -1) +
      labs(title = "Posterior SD (Gaussian BYM2)") +
      theme_minimal() +
      theme(
        legend.position = "right",
        plot.title = element_text(face = "bold"),
        panel.grid.major = element_line(linewidth = 0.1, linetype = "dotted")
      )
    pa_sd

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Plot%20results%20-%20Gaussian-2.png)

    pa_ci <- ggplot(sf_a) +
      geom_sf(aes(fill = fit_ci), color = "grey", linewidth = 0.01) +
      scale_fill_distiller(name = "Posterior 95% CI Width", palette = "RdYlBu", direction = -1) +
      labs(title = "Posterior 95% CI Width (Poisson BYM2)") +
      theme_minimal() +
      theme(
        legend.position = "right",
        plot.title = element_text(face = "bold"),
        panel.grid.major = element_line(linewidth = 0.1, linetype = "dotted")
      )
    pa_ci

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Plot%20results%20-%20Gaussian-3.png)

### Plot the results from the Poisson BYM2 Spatial Model

    ### Start from the same data frame
    ### Create new R object

    sf_b <- fc_df

    ### Extract fitted values from Poisson model

    sum_b <- fit_b$summary.fitted.values
    sf_b$fit_mean_cnt <- sum_b$mean
    sf_b$fit_lcl_cnt <- sum_b$`0.025quant`
    sf_b$fit_ucl_cnt <- sum_b$`0.975quant`
    sf_b$fit_sd_cnt <- sum_b$sd

    ### Convert to rates per 100,000

    sf_b$fit_mean_rate <- (sf_b$fit_mean_cnt / sf_b$TOT_POP) * 1e5
    sf_b$fit_lcl_rate <- (sf_b$fit_lcl_cnt / sf_b$TOT_POP) * 1e5
    sf_b$fit_ucl_rate <- (sf_b$fit_ucl_cnt / sf_b$TOT_POP) * 1e5
    sf_b$fit_ci_rate <- sf_b$fit_ucl_rate - sf_b$fit_lcl_rate
    sf_b$fit_sd_rate <- (sf_b$fit_sd_cnt / sf_b$TOT_POP) * 1e5

    ### Posterior mean map (Poisson)

    pb_mean <- ggplot(sf_b) +
      geom_sf(aes(fill = fit_mean_rate), color = "grey", linewidth = 0.01) +
      scale_fill_distiller(
        name = "Posterior Mean",
        palette = "RdYlBu",
        direction = -1
      ) +
      labs(title = "Posterior Mean (Poisson BYM2)") +
      theme_minimal() +
      theme(
        legend.position = "right",
        plot.title = element_text(face = "bold"),
        panel.grid.major = element_line(linewidth = 0.1, linetype = "dotted")
      )
    pb_mean

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Plot%20results%20-%20Poisson-1.png)

    ### Posterior SD map (Poisson)

    pb_sd <- ggplot(sf_b) +
      geom_sf(aes(fill = fit_sd_rate), color = "grey", linewidth = 0.01) +
      scale_fill_distiller(
        name = "Posterior SD",
        palette = "RdYlBu",
        direction = -1
      ) +
      labs(title = "Posterior SD (Poisson BYM2)") +
      theme_minimal() +
      theme(
        legend.position = "right",
        plot.title = element_text(face = "bold"),
        panel.grid.major = element_line(linewidth = 0.1, linetype = "dotted")
      )
    pb_sd

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Plot%20results%20-%20Poisson-2.png)

    ### Posterior CI width map (Poisson)

    pb_ci <- ggplot(sf_b) +
      geom_sf(aes(fill = fit_ci_rate), color = "grey", linewidth = 0.01) +
      scale_fill_distiller(
        name = "Posterior 95% CI Width",
        palette = "RdYlBu",
        direction = -1
      ) +
      labs(title = "Posterior 95% CI Width (Poisson BYM2)") +
      theme_minimal() +
      theme(
        legend.position = "right",
        plot.title = element_text(face = "bold"),
        panel.grid.major = element_line(linewidth = 0.1, linetype = "dotted")
      )
    pb_ci

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Plot%20results%20-%20Poisson-3.png)

### Diagnostics from the spatial models

    ### Diagnostics - Gaussian model

    ### R-Squared (Gaussian model)

    y_obs_gauss <- df_model_annual[[resp_var]]

    y_hat_gauss <- fit_a$summary.fitted.values$mean

    r_squared_gauss <- cor(
      y_obs_gauss,
      y_hat_gauss,
      use = "complete.obs")^2

    print(paste("Gaussian R-Squared: ", round(r_squared_gauss, 3)))

    ## [1] "Gaussian R-Squared:  0.261"

    ### RMSE (Gaussian model)

    rmse_gauss <- sqrt(mean(
      (df_model_annual[[resp_var]] - fit_a$summary.fitted.values$mean)^2,
      na.rm = T
    ))
    print(paste("Gaussian RMSE: ", round(rmse_gauss, 3)))

    ## [1] "Gaussian RMSE:  194.223"

    ### 95% Predictive Coverage (Gaussian model)

    coverage95_gauss <- mean(
      df_model_annual[[resp_var]] >= fit_a$summary.fitted.values$`0.025quant` &
      df_model_annual[[resp_var]] <= fit_a$summary.fitted.values$`0.975quant`,
      na.rm = T
    )
    print(paste("Gaussian 95% coverage: ", round(coverage95_gauss, 3)))

    ## [1] "Gaussian 95% coverage:  0.345"

    ### DIC (Gaussian model)

    print(paste("Gaussian DIC: ", round(fit_a$dic$dic, 3)))

    ## [1] "Gaussian DIC:  779.132"

    ### WAIC (Gaussian model)

    print(paste("Gaussian WAIC: ", round(fit_a$waic$waic, 3)))

    ## [1] "Gaussian WAIC:  779.54"

    ### Diagnostics - Poisson model

    y_obs_rate <- df_model_annual[[resp_var]]

    pop_vec <- fc_no_geom$TOT_POP

    mu_hat_pois <- fit_b$summary.fitted.values$mean

    lcl_pois <- fit_b$summary.fitted.values$`0.025quant`

    ucl_pois <- fit_b$summary.fitted.values$`0.975quant`

    ### Convert expected counts and intervals to rates

    y_hat_pois_rate <- (mu_hat_pois / pop_vec) * 1e5

    lcl_pois_rate <- (lcl_pois / pop_vec) * 1e5

    ucl_pois_rate <- (ucl_pois / pop_vec) * 1e5

    ### R-Squared (Poisson model)

    y_obs_rate <- df_model_annual[[resp_var]]

    y_hat_pois_rate <- (fit_b$summary.fitted.values$mean / fc_no_geom$TOT_POP) * 1e5

    r_squared_pois <- cor(
      y_obs_rate, 
      y_hat_pois_rate,
      use = "complete.obs")^2

    print(paste("Poisson R-Squared (rate scale): ", round(r_squared_pois, 3)))

    ## [1] "Poisson R-Squared (rate scale):  0.962"

    ### RMSE (Poisson model)

    rmse_pois <- sqrt(mean(
      (y_obs_rate - y_hat_pois_rate)^2,
      na.rm = T
    ))
    print(paste("Poisson RMSE: ", round(rmse_pois, 3)))

    ## [1] "Poisson RMSE:  40.42"

    ### 95% Predictive Coverage (Poisson model)

    coverage95_pois <- mean(
      y_obs_rate >= lcl_pois_rate &
        y_obs_rate <= ucl_pois_rate,
      na.rm = T
    )
    print(paste("Poisson 95% coverage: ", round(coverage95_pois, 3)))

    ## [1] "Poisson 95% coverage:  0.983"

    ### DIC (Poisson model)

    print(paste("Poisson DIC: ", round(fit_b$dic$dic, 3)))

    ## [1] "Poisson DIC:  612.796"

    ### WAIC (Poisson model)

    print(paste("Poisson WAIC: ", round(fit_b$waic$waic, 3)))

    ## [1] "Poisson WAIC:  599.94"

### Residual map - Gaussian

    ### Residual diagnostics for Gaussian model

    ### Compute residuals in the model frame

    df_model_annual$residuals <- df_model_annual[[resp_var]] -
      fit_a$summary.fitted.values$mean

    sf_resid <- fc_df

    sf_resid$residuals <- df_model_annual$residuals

    ggplot(sf_resid) +
      geom_sf(aes(fill = residuals), color="grey", linewidth = 0.01) +
      scale_fill_distiller(palette = "RdYlBu") +
      labs(title="Residual Map (Gaussian BYM2)", fill = "Pearson Residual") +
      theme_minimal()

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Residual%20Map%20and%20residual%20hotspot%20map%20-%20Gaussian-1.png)

    ### Spatial autocorrelation in residuals

    nb_resid <- poly2nb(as_Spatial(fc_df))
    lw_resid <- nb2listw(nb_resid, style = "W", zero.policy = T)

    moran_res <- moran.test(sf_resid$residuals, lw_resid, zero.policy = T)

    print(moran_res)

    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  sf_resid$residuals  
    ## weights: lw_resid    
    ## 
    ## Moran I statistic standard deviate = 2.513, p-value = 0.005985
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##       0.190313105      -0.017543860       0.006841335

    ### Local Moran's I 

    lm_res <- localmoran(sf_resid$residuals,
                         lw_resid,
                         zero.policy = T)

    ### Add results to the sf object

    sf_resid$Ii <- lm_res[, "Ii"]
    sf_resid$Z_Ii <- lm_res[, "Z.Ii"]
    sf_resid$p_Ii <- 2 * pnorm(-abs(sf_resid$Z_Ii))

    ### Spatial lag of residuals

    lag_resid <- lag.listw(lw_resid,
                           sf_resid$residuals,
                           zero.policy = T)

    mean_resid <- mean(sf_resid$residuals, na.rm = T)

    mean_lag <- mean(lag_resid, na.rm = T)

    sf_resid$cluster <- "Not significant"

    sig <- sf_resid$p_Ii <= 0.05

    sf_resid$cluster[sig & sf_resid$residuals >  mean_resid & lag_resid >  mean_lag] <- "High-High"
    sf_resid$cluster[sig & sf_resid$residuals <  mean_resid & lag_resid <  mean_lag] <- "Low-Low"
    sf_resid$cluster[sig & sf_resid$residuals >  mean_resid & lag_resid <  mean_lag] <- "High-Low"
    sf_resid$cluster[sig & sf_resid$residuals <  mean_resid & lag_resid >  mean_lag] <- "Low-High"

    sf_resid$cluster <- factor(
      sf_resid$cluster,
      levels = c("High-High", "Low-Low", "High-Low", "Low-High", "Not significant"))

    ### Local Moran's I plot

    ggplot(sf_resid) +
      geom_sf(aes(fill = cluster), color = "grey", linewidth = 0.01) +
      scale_fill_manual(
        name = "cluster",
        values = c(
          "High-High" = "#b2182b",
          "Low-Low" = "#2166ac",
          "High-Low" = "#ef8a62",
          "Low-High" = "#67a9cf",
          "Not significant"= "white"
        )) +
      labs (
        title = "Local Moran's I Cluster Map of Residuals",
        subtitle = "Respiratory Mortality (Gaussian BYM2)"
      ) +
      theme_minimal()

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Residual%20Map%20and%20residual%20hotspot%20map%20-%20Gaussian-2.png)

### Residual map - Poisson

    ### Pearson residuals for Poisson model

    ### Observed counts and fitted counts

    y_count   <- fc_no_geom$resp_deaths

    mu_hat_b  <- fit_b$summary.fitted.values$mean

    ### Pearson residuals

    df_model_annual$resid_pois <- (y_count - mu_hat_b) / sqrt(mu_hat_b)

    sf_resid_p <- fc_df

    sf_resid_p$resid_pois <- df_model_annual$resid_pois

    ### Residual map

    ggplot(sf_resid_p) +
      geom_sf(aes(fill = resid_pois), color = "grey", linewidth = 0.01) +
      scale_fill_distiller(palette = "RdYlBu") +
      labs(
        title = "Residual Map (Poisson BYM2)",
        fill  = "Pearson Residual"
      ) +
      theme_minimal()

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Residual%20Map%20and%20residual%20hotspot%20map%20-%20Poisson-1.png)

    ### Spatial autocorrelation in Poisson residuals

    nb_resid <- poly2nb(as_Spatial(fc_df))
    lw_resid <- nb2listw(nb_resid, style = "W", zero.policy = T)

    moran_res_pois <- moran.test(sf_resid_p$resid_pois, lw_resid, zero.policy = T)
    print(moran_res_pois)

    ## 
    ##  Moran I test under randomisation
    ## 
    ## data:  sf_resid_p$resid_pois  
    ## weights: lw_resid    
    ## 
    ## Moran I statistic standard deviate = 0.029389, p-value = 0.4883
    ## alternative hypothesis: greater
    ## sample estimates:
    ## Moran I statistic       Expectation          Variance 
    ##      -0.015743434      -0.017543860       0.003752947

    ### Local Moran's I for Poisson residuals

    lm_res_p <- localmoran(sf_resid_p$resid_pois,
                           lw_resid,
                           zero.policy = T)

    sf_resid_p$Ii   <- lm_res_p[, "Ii"]
    sf_resid_p$Z_Ii <- lm_res_p[, "Z.Ii"]
    sf_resid_p$p_Ii <- 2 * pnorm(-abs(sf_resid_p$Z_Ii))

    ### Spatial lag of residuals

    lag_resid_p <- lag.listw(lw_resid,
                             sf_resid_p$resid_pois,
                             zero.policy = T)

    mean_resid_p <- mean(sf_resid_p$resid_pois, na.rm = T)
    mean_lag_p <- mean(lag_resid_p, na.rm = T)

    sf_resid_p$cluster <- "Not significant"
    sig_p <- sf_resid_p$p_Ii <= 0.05

    sf_resid_p$cluster[sig_p & sf_resid_p$resid_pois >  mean_resid_p & lag_resid_p >  mean_lag_p] <- "High-High"
    sf_resid_p$cluster[sig_p & sf_resid_p$resid_pois <  mean_resid_p & lag_resid_p <  mean_lag_p] <- "Low-Low"
    sf_resid_p$cluster[sig_p & sf_resid_p$resid_pois >  mean_resid_p & lag_resid_p <  mean_lag_p] <- "High-Low"
    sf_resid_p$cluster[sig_p & sf_resid_p$resid_pois <  mean_resid_p & lag_resid_p >  mean_lag_p] <- "Low-High"

    sf_resid_p$cluster <- factor(
      sf_resid_p$cluster,
      levels = c("High-High", "Low-Low", "High-Low", "Low-High", "Not significant")
    )

    ggplot(sf_resid_p) +
      geom_sf(aes(fill = cluster), color = "grey", linewidth = 0.01) +
      scale_fill_manual(
        name = "Cluster",
        values = c(
          "High-High" = "#b2182b",
          "Low-Low" = "#2166ac",
          "High-Low"= "#ef8a62",
          "Low-High" = "#67a9cf",
          "Not significant" = "white"
        )
      ) +
      labs(
        title = "Local Moran's I Cluster Map of Residuals",
        subtitle = "Respiratory Mortality (Poisson BYM2)"
      ) +
      theme_minimal()

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Residual%20Map%20and%20residual%20hotspot%20map%20-%20Poisson-2.png)

### Predicted vs observed plot

    ### Posterior predictive distribution vs observed

    post_mean <- fit_a$summary.fitted.values$mean

    ggplot() +
      geom_point(aes(x = post_mean, y = df_model_annual[[resp_var]]),
                 color = "navy", alpha = 0.5) +
      geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
      labs(
        title = "Posterior Predictive Plot (Gaussian BYM2)",
        x = "Predicted rate (per 100,000)",
        y = "Observed rate (per 100,000)"
      ) +
      theme_minimal()

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Posterior%20Predictive%20Check-1.png)

    ### Predicted rate from Poisson (per 100,000)

    lp_b <- fit_b$summary.linear.predictor
    mu_hat_b <- exp(lp_b$mean)

    pop_vec <- fc_no_geom$TOT_POP
    y_hat_rate_pois <- (mu_hat_b / pop_vec) * 1e5
    y_obs_rate <- df_model_annual[[resp_var]]

    ggplot() +
      geom_point(aes(x = y_hat_rate_pois, y = y_obs_rate),
                 color = "navy", alpha = 0.5) +
      geom_abline(slope = 1, intercept = 0,
                  color = "red", linetype = "dashed") +
      labs(
        title = "Posterior Predictive Plot (Poisson BYM2)",
        x = "Predicted rate (per 100,000)",
        y = "Observed rate (per 100,000)"
      ) +
      theme_minimal()

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Posterior%20Predictive%20Check-2.png)

### Plot the posterior distribution

    ### Posterior predictive density for respiratory mortality rate

    ### Set seed for reproducability

    set.seed(123)

    ### Extract fitted means

    sum_a <- fit_a$summary.fitted.values

    ### Observed respiratory mortality

    y_obs <- df_model_annual[[resp_var]]

    ### Sample from the posterior

    prec_marg <- fit_a$marginals.hyperpar[["Precision for the Gaussian observations"]]

    n_samp <- 5000

    prec_samp <- inla.rmarginal(n_samp, prec_marg)

    sigma_samp <- 1 / sqrt(prec_samp)

    ### Combine with the fitted means to generate posterior predictive draws

    n_areas <- nrow(sum_a)

    idx_samp <- sample.int(n_areas, size = n_samp, replace = T)

    mu_samp <- sum_a$mean[idx_samp]

    y_rep <- rnorm(n_samp, mean = mu_samp, sd = sigma_samp)

    ### Build data frames for plotting

    df_post <- data.frame(
      value = y_rep,
      type = "Posterior distribution"
    )

    df_obs <- data.frame(
      value = y_obs,
      type  = "Observed"
    )

    df_plot <- rbind(df_post, df_obs)

    ### Density plot: posterior predictive vs observed

    ggplot(df_plot, aes(x = value, fill = type)) +
      geom_density(alpha = 0.5) +
      labs(
        title = "Posterior Density Plot",
        x = "Respiratory Mortality Rate",
        y = "Density",
        fill  = ""
      ) +
      theme_minimal()

![](CAPSTONE_Project_JacobAnderson_files/figure-markdown_strict/Posterior%20Density%20Plot-1.png)

**This study demonstrates that Bayesian spatial modeling provides an
effective framework for examining ozone-related respiratory mortality
while accounting for geographic dependence. The Gaussian model captured
broad patterns and generated modest predictive performance, but much of
the spatial structure remained unexplained. The Poisson BYM2 model,
assisted by a log scaled offset for population and an appropriate
incident count based likelihood, illuminated clear advantages over the
Gaussian BYM2 model: improved predictive performance, better uncertainty
calibration, and adequate handling of spatial autocorrelation for the
residual estimates. Posterior mean surfaces from both models displayed
strong regional variation in respiratory mortality risk, with elevated
rates in northern and central California.**

**These findings suggest that Poisson spatial model is more appropriate
for county level mortality modeling and should be favored in future
environmental health analyses and research. In future work,
incorporating multiple years of NASA TEMPO ozone data, validating ozone
conversion methods, integrating detailed socioeconomic indicators, and
expanding to fully spatiotemporal Bayesian models could provide a more
detailed understanding of air pollution interaction with demographic and
climatic factors to influence respiratory health across California.**
