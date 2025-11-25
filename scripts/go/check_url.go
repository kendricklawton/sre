package main

import (
	"fmt"
	"net/http"
	"sync"
	"time"
)

func checkUrl(url string, wg *sync.WaitGroup, results chan<- string) {
	defer wg.Done() // 1. Signal completion

	// 2. Create a Client with Timeout
	client := http.Client{
		Timeout: 5 * time.Second,
	}

	// 3. Perform the Request
	resp, err := client.Get(url)
	if err != nil {
		results <- fmt.Sprintf("[FAIL] %s - Error: %v", url, err)
		return
	}
	defer resp.Body.Close() // 4. Cleanup

	// 5. Send Success
	results <- fmt.Sprintf("[%s] %s - Status: %d", "SUCCESS", url, resp.StatusCode)
}
