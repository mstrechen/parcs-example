package main

import (
	"github.com/lionell/parcs/go/parcs"
	"log"
	"time"
)

type LargestCommonSubsequence struct {
	*parcs.Service
}

func Max(x, y int) int {
	if x < y {
		return y
	}
	return x
}

func getLCSS(s, t string) []int{
	n := len(s)
	m := len(t)
	previousLevel := make([]int, m + 1)
	currentLevel := make([]int, m + 1)

	for i := 0; i < n; i++ {
	    for j := 0; j < m; j++ {
	    	currentLevel[j + 1] = Max(previousLevel[j + 1], currentLevel[j])
	        if s[i] == t[j] {
				currentLevel[j + 1] = previousLevel[j] + 1
			}
	    }
	    currentLevel, previousLevel = previousLevel, currentLevel
	}
	return previousLevel
}


func getFullResult(s, t string) ([][]int, time.Duration) {
	var execTime time.Duration
	start := time.Now()
	defer func() {
		execTime = time.Since(start)
	}()

	var result = make([][]int, len(t))
	m := len(t)

	for suffixIn := range t {
		partialResult := getLCSS(s, t[suffixIn:])
		result[suffixIn] = make([]int, m)
		for i := 0; i < suffixIn; i++ {
			result[suffixIn][i] = 0
		}
		for i := suffixIn; i < m; i++ {
			result[suffixIn][i] = partialResult[i - suffixIn]
		}
	}

	return result, execTime
}

type Result struct {
	Result [][]int
	ExecutionTime string
}

func (e *LargestCommonSubsequence) Run() {
	var s string
	var t string

	log.Print("Receiving strings s, t")

	if err := e.Recv(&s); err != nil {
		panic("Error while receiving string s")
	}

	if err := e.Recv(&t); err != nil {
		panic("Error while receiving string t")
	}

	log.Printf("Received s, t. Calculating...")

	result, execTime := getFullResult(s, t)

	log.Printf("Sending result...")

    err := e.Send(Result{
		Result:result, ExecutionTime: execTime.String(),
	})
	if err != nil {
		panic("Error during sending result")
	}
}

func main() {
	parcs.Exec(&LargestCommonSubsequence{parcs.DefaultService()})
}
