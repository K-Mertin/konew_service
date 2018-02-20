from DataAccess import DataAccess
import pymongo

class loancaseAccess(DataAccess):
    def add_loancase(self, loancase):
        self.logger.logger.info('add loancase')
        return self.db['Loancases'].insert(loancase)

    def get_allPaged_loancases(self, pageSize=10, pageNum=1):
       skips = pageSize * (pageNum - 1)
       
       totalCount = self.db['Loancases'].find().count()

       result = {
           "totalCount":totalCount,
           "data": self.db['Loancases'].find().sort("createDate", pymongo.DESCENDING).skip(skips).limit(pageSize)
       }
       return result


if __name__ == "__main__":
    db = loancaseAccess()
