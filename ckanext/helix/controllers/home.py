import ckan.lib.base as base

class Controller(base.BaseController):
    
    def faq(self):
        return base.render('home/faq.html')