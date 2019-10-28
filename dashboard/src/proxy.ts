/*
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Programmable Proxy Server in a single Python file.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
*/
import {WebsocketApi} from "./inspect"
import {ApiDevelopment} from "./api"
import {Home} from "./home"
import {ShortLinks} from "./shortLinks"
import {Controls} from "./controls"
import {Settings} from "./settings"


export class ProxyDashboard {
  
  private home : Home
  private apiDevelopment: ApiDevelopment
  private websocketApi: WebsocketApi
  private shortLinks: ShortLinks
  private controls: Controls
  private settings: Settings 

  constructor () {
   
    const that = this
    $('#proxyTopNav>ul>li>a').on('click', function () {
      that.switchTab(this)
    })
    this.home = new Home();
    this.apiDevelopment = new ApiDevelopment();
    this.websocketApi = new WebsocketApi()
    this.shortLinks = new ShortLinks();
    this.controls = new Controls();
    this.settings = new Settings();
  }

  public static getTime () {
    const date = new Date()
    return date.getTime()
  }

  public static setServerStatusDanger () {
    $('#proxyServerStatus').parent('div')
      .removeClass('text-success')
      .addClass('text-danger')
    $('#proxyServerStatusSummary').text('')
  }

  public static setServerStatusSuccess (summary: string) {
    $('#proxyServerStatus').parent('div')
      .removeClass('text-danger')
      .addClass('text-success')
    $('#proxyServerStatusSummary').text(
      '(' + summary + ')')
  }

  private switchTab (element: HTMLElement) {
    const activeLi = $('#proxyTopNav>ul>li.active')
    const activeTabId = activeLi.children('a').attr('id')
    const clickedTabId = $(element).attr('id')
    const clickedTabContentId = $(element).text().trim().toLowerCase().replace(' ', '-')

    activeLi.removeClass('active')
    $(element.parentNode).addClass('active')
    console.log('Clicked id %s, showing %s', clickedTabId, clickedTabContentId)

    $('#app>div.proxy-data').hide()
    $('#' + clickedTabContentId).show()

    // TODO: Tab ids shouldn't be hardcoded.
    // Templatize proxy.html and refer to tab_id via enum or constants
    //
    // 1. Enable inspection if user moved to inspect tab
    // 2. Disable inspection if user moved away from inspect tab
    // 3. Do nothing if activeTabId == clickedTabId
    if (clickedTabId !== activeTabId) {
      //deactivateAll
      this.home.disable();
      this.apiDevelopment.disable();
      this.websocketApi.disable();  
      this.shortLinks.disable();
      this.controls.disable();
      this.settings.disable();

      switch(clickedTabId) {
        case "proxyHome": 
          this.home.enable()
          break;
        case "proxyApiDevelopment":
          this.apiDevelopment.enable()
          break;
        case "proxyInspect":
          this.websocketApi.enable()
          break;
        case "proxyShortLinks":
          this.shortLinks.enable();
          break;
        case "proxyControls":
            this.controls.enable()
          break;
        case "proxySettings":
          this.settings.enable();
          break;
      }

    }
  }



}

(window as any).ProxyDashboard = ProxyDashboard
