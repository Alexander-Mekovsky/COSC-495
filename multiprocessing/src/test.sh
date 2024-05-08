#!/bin/bash

# Start timing the script
start_time=$(date +%s)

# Function to send requests and print timing
send_request() {
    baseUrl="https://api.elsevier.com/content/search/scopus"
    queryParams="query=all(climate%20change%20global%20warming%20ocean%20atmosphere)"
    additionalParams="&sort=coverDate&count=25&apiKey=3e98ccbfff5ed19b801086b00dfc5e36&view=standard&xml-decode=true&httpAccept=application/xml"

    start=$1
    fullUrl="${baseUrl}?${queryParams}&start=${start}${additionalParams}"
    
    # Send request and print only the total time taken
    curl -o /dev/null -s -w "Request at start=${start}: Time taken = %{time_total}s\n" \
         -H "Connection: keep-alive" -H "Accept: application/xml" "${fullUrl}"
}

export -f send_request

# Generate reverse sequence and call send_request function in parallel
seq 1000 -25 150 | xargs -I {} -P 8 -n 1 bash -c 'send_request "$@"' _ {}

# End timing the script and calculate total duration
end_time=$(date +%s)
echo "Total execution time: $((end_time - start_time)) seconds"
