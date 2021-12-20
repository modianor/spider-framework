import json

from core.policy import Policy
from core.task import Task
from fetcher import Fetcher


class CommonFetcher(Fetcher):
    def __init__(self) -> None:
        super().__init__()

    def setPolicy(self, policy: Policy):
        super().setPolicy(policy)

    def getList(self, task: Task):
        urlList = []
        preHtml = ''
        urlSign = json.loads(task.urlSign)
        url = urlSign.get("url", "")
        commonConfig = json.loads(task.companyName)
        pageParseConfig = commonConfig.get("pageParse", {})
        pageStart = pageParseConfig.get("pageStart", 1)
        pageBegin = pageParseConfig.get("pageBegin", 2)
        pageNums = pageParseConfig.get("pageNums", {})
        sameDiff = pageParseConfig.get("diff", 0.99)
        if "autoPage" in pageParseConfig and pageParseConfig["autoPage"]:
            # 自动翻页
            preUrl = url.format_map({"pageNums": pageStart})
            preHtml = ''
            # 这里做解析保存处理
            for i in range(pageBegin, 10000000000):
                curUrl = url.format_map({"pageNums": pageStart})
                curHtml = ''
                threshold = .8
                if threshold > sameDiff:
                    # 相似度超过阈值 出现重复了
                    break
                else:
                    # 继续翻页
                    preHtml = curHtml
                    continue

            # 请求访问 比较和前一个页面的相似度
            # 如果相似度超过阈值 则自动翻页结束
            # 如果相似度没有超过阈值，则继续翻页
        else:
            # 手动解析
            if "pageNums" in pageParseConfig:
                # 手动指定或者规则化抽取
                while True:
                    # 如果请求队列为空 则跳出
                    # 如果请求队列不为空 则继续消费层请求队列
                    pageNums = 10
                    mainUrl = url.format_map({"pageNums": pageStart})
                    urlList.append(mainUrl)
                    for i in range(pageBegin, pageNums):
                        mainUrl = url.format_map({"pageNums": pageStart})
                        html = ''
                        # 这里生成Detail任务 保存
                    break

    def getDetail(self, task: Task):
        pass

    def getData(self, task: Task):
        pass
