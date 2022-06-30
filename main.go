package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

func main() {
	getAllChapterLink("8969")
}

type image struct {
	filename  string
	chapter   string
	titleID   string
	titleName string
	link      string
}

func getImageLink(filename string, chapter string, titleID string) string {
	return fmt.Sprintf("https://www.osemocphoto.com/collectManga/%s/%s/%s", titleID, chapter, filename)
}

func getRespones(link string) (*http.Response, error) {
	client := http.Client{
		Timeout: time.Second * 10,
	}
	req, err := http.NewRequest("GET", link, nil)
	req.Header.Set("Referer", "https://www.nekopost.net/")
	req.Header.Set("Host", "www.osemocphoto.com")
	if err != nil {
		log.Fatal(err)
	}
	return client.Do(req)

}

func download(i image, wg *sync.WaitGroup) {
	createFolder(i.titleName)
	folder := i.titleName + "/" + i.chapter
	createFolder(folder)
	filePath := folder + "/" + i.filename
	resp, err := getRespones(i.link)
	count := 0
	for resp.StatusCode == 520 && count < 5 {
		time.Sleep(time.Millisecond * 3000)
		resp, err = getRespones(i.link)
		count++
	}
	if resp.StatusCode == 520 {
		log.Printf("dowload failed: %s", i.filename)
		return
	}
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	file, err := os.Create(filePath)
	if err != nil {
		log.Fatal(err)
	}
	_, err = io.Copy(file, resp.Body)
	//fmt.Println("Download success:", filePath)
	if err != nil {
		log.Fatal(err)
	}
	wg.Done()
}

type Chapter struct {
	title     string
	name      string
	chapter   string
	chapterID string
	link      string
}

func getChapterLinks(titleID string, chapterID string) string {
	return fmt.Sprintf("https://www.osemocphoto.com/collectManga/%s/%s/%s_%s.json", titleID, chapterID, titleID, chapterID)
}

func getAllChapterLink(titleID string) {
	client := http.Client{
		Timeout: time.Second * 3,
	}
	link := fmt.Sprintf("https://api.osemocphoto.com/frontAPI/getProjectInfo/%s", titleID)
	resp, err := client.Get(link)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	body, readErr := ioutil.ReadAll(resp.Body)
	if readErr != nil {
		log.Fatal(readErr)
	}

	var data map[string]interface{}
	err = json.Unmarshal(body, &data)
	if err != nil {
		log.Fatal(err)
	}

	chaptersList := data["listChapter"].([]interface{})
	name, ok := data["projectInfo"].(map[string]interface{})["projectName"]
	if !ok {
		log.Fatal("can't find project name !")
	}
	fmt.Println(name)

	chapters := map[string]Chapter{}
	for _, c := range chaptersList {
		chapterNo := c.(map[string]interface{})["chapterNo"].(string)
		chapterID := c.(map[string]interface{})["chapterId"].(string)
		ch := Chapter{
			name:      name.(string),
			chapter:   c.(map[string]interface{})["chapterNo"].(string),
			chapterID: chapterID,
			title:     titleID,
			link:      getChapterLinks(titleID, chapterID),
		}
		chapters[chapterNo] = ch
	}

	var mainWG sync.WaitGroup
	mainWG.Add(len(chapters))
	for _, c := range chapters {
		go getChapter(c, &mainWG)
	}
	mainWG.Wait()
}

type respJson struct {
	PageItem []struct {
		PageName string `json:"pageName"`
		FileName string `json:"fileName"`
	} `json:"pageItem"`
}

func createFolder(name string) {
	if err := os.Mkdir(name, os.ModePerm); err != nil {
		if os.IsExist(err) {
			return
		}
		log.Fatal(err)
	}
}

func getChapter(chapter Chapter, mainWG *sync.WaitGroup) {
	client := http.Client{
		Timeout: time.Second * 3,
	}
	resp, err := client.Get(chapter.link)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}
	var data respJson
	json.Unmarshal(body, &data)

	pages := data.PageItem
	var wg sync.WaitGroup
	wg.Add(len(pages))
	for _, page := range pages {
		var filename string
		if page.PageName == "" {
			filename = page.FileName
		} else {
			filename = page.PageName
		}
		i := image{
			chapter:   chapter.chapter,
			link:      getImageLink(filename, chapter.chapterID, chapter.title),
			filename:  filename,
			titleID:   chapter.title,
			titleName: chapter.name,
		}
		go download(i, &wg)
	}
	wg.Wait()
	fmt.Printf("Chapter %s dowload success \n", chapter.chapter)
	mainWG.Done()
}
