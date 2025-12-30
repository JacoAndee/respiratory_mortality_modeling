### Fetch API key and search for variables

library(tidycensus)

tidycensus::census_api_key(key = "CENSUS_API_KEY",
                           install = T, 
                           overwrite = T)
v22 <- load_variables(year = 2024,
                      dataset = "acs1/profile",
                      cache = T)
vars = c("B01001_001E", "B01001_003E", "B01001_027E", "B01001_020E", 
         "B01001_021E", "B01001_022E", "B01001_023E", "B01001_024E", 
         "B01001_025E", "B01001_044E", "B01001_045E", "B01001_046E", 
         "B01001_047E", "B01001_048E", "B01001_049E", "B17020_001E")
ca_acs <- get_acs(geography = "county",
                  state = "CA",
                  variables = vars,
                  year = 2024,
                  geometry = F,
                  output = "wide",
                  survey = "acs1"
)
ca_acs_df <- write.csv(ca_acs, 
                       "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ACS/acs_pop_variables_2024.csv")
