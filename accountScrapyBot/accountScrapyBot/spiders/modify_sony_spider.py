#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

from scrapy.selector import Selector

from accountScrapyBot.items import AccountscrapybotItem

# Color logging
from colorama import Fore, Back, Style, init
init(autoreset=True)

# URLS
url_mediadevices = "https://account.sonyentertainmentnetwork.com/liquid/cam/devices/device-media-list.action"
url_logout = "https://account.sonyentertainmentnetwork.com/liquid/j_spring_security_logout"
url_changepass = "https://account.sonyentertainmentnetwork.com/liquid/cam/account/profile/edit-password!input.action"

# Variables
first_pass = "ML2016games"
second_pass = "ML2017games"
third_pass = "ML2018games"
final_pass = "ML1986games"

user_test = "ps3bo37288@g4m3s.co"
pass_test = "ML2017games"



class AccountSpider(scrapy.Spider):
    name = 'accountScrapyBot'
    start_urls = ['https://account.sonyentertainmentnetwork.com/liquid/login.action']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'j_username': user_test, 'j_password': pass_test},
            callback=self.after_login
        )

    def after_login(self, response):
        # check login succeed before going on
        if "Account Details" in response.body:
            self.logger.error(Fore.GREEN + "Login EXITO")
            yield scrapy.Request(url_mediadevices, self.checkMediaDevices)
        elif "suspended" in response.body:
        	self.logger.error(Fore.RED + "Cuenta Suspendida")
        elif "login" in response.body:
        	self.logger.error(Fore.RED + "Clave INCORRECTA")
        return

        # continue scraping with authenticated session...
    def changePassFirstTime(self, response):
    	""" change pass on account activated once > first_pass
    	"""
    	if pass_test == first_pass:
            self.logger.error(Fore.GREEN + "PASS ESTA OK")    		
    	else:
	        yield scrapy.FormRequest.from_response(
	        	response,
	            formdata={'currentPassword': pass_test, 'password': first_pass, 'confirmPassword': first_pass },
	            callback=self.after_changepass
	            )

    def changePassSecondTime(self, response):
    	""" change pass on account desactivated > second_pass
    	"""
    	if pass_test == second_pass:
            self.logger.error(Fore.GREEN + "PASS ESTA OK")    		
    	else:
    		yield scrapy.FormRequest.from_response(
	        	response,
	            formdata={'currentPassword': pass_test, 'password': second_pass, 'confirmPassword': second_pass },
	            callback=self.after_changepass
	            )

    def changePassThirdTime(self, response):
    	""" change pass on account desactivated and activated once > third_pass
    	"""
    	if pass_test == third_pass:
            self.logger.error(Fore.GREEN + "PASS ESTA OK")    		
    	else:
    		yield scrapy.FormRequest.from_response(
        	response,
            formdata={'currentPassword': pass_test, 'password': third_pass, 'confirmPassword': third_pass },
            callback=self.after_changepass
            )

    def changePassFinalTime(self, response):
    	""" change pass on account activated desactivated and activated twice > final_pass
    	"""
        if pass_test == first_pass:
            self.logger.error(Fore.GREEN + "PASS ESTA OK")    		
    	else:
	        yield scrapy.FormRequest.from_response(
        	response,
            formdata={'currentPassword': pass_test, 'password': final_pass, 'confirmPassword': final_pass },
            callback=self.after_changepass
            )

    def after_changepass(self, response):
        # check login succeed before going on
        #//*[@id="toutLabel"]
        if 'Your password has been saved.'in response.body:
            self.logger.error(Fore.GREEN + "PASS cambiado")
            yield scrapy.Request(url_logout)
        else:
        	self.logger.error(Fore.RED + "Pass ERROR")
        	yield scrapy.Request(url_logout)
        return


    def checkMediaDevices(self, response):
    	""" check activated devices: 1 > change pass, 2 or more > deactivate and change pass
    	"""
    	item = AccountscrapybotItem()
    	sel = Selector(response)
        item['activations'] = sel.xpath('//*[@id="gameMediaDevicesDeactivateSection"]/label[2]/text()').extract()
        if item['activations'][0] == u"None":
        	if "deactivated" in response.body:
        		self.logger.error(Fore.GREEN + "2 ACTIVAS Y RECIEN DESACTIVADA")    		
        		yield scrapy.Request(url_changepass, 
                callback=self.changePassSecondTime
                )
        	else:
        		self.logger.error(Fore.GREEN + "Cuenta SIN activar")    		
        		yield scrapy.Request(url_logout)
        elif item['activations'][0] == u"1 PlayStation® Systems":
        	if "deactivated" in response.body:
        		self.logger.error(Fore.GREEN + "1 ACTIVA YA DESACTIVADA")    		
        		yield scrapy.Request(url_changepass, 
                callback=self.changePassThirdTime
                )
        	else:
        		self.logger.error(Fore.GREEN + "1 ACTIVA")    		
        		yield scrapy.Request(url_changepass, 
                callback=self.changePassFirstTime
                )
        elif item['activations'][0] == u"2 PlayStation® Systems":
        	if "deactivated" in response.body:
        		self.logger.error(Fore.GREEN + "4 ACTIVADAS VA A ARCHIVO")    		
        		yield scrapy.Request(url_changepass, 
                callback=self.changePassFinalTime
                )
        	else:
        		self.logger.error(Fore.GREEN + "2 ACTIVAS SIN DESACTIVAR")    		
        		yield scrapy.Request(url_logout)
        return

    