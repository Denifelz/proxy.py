/*
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Programmable, TLS interception capable
    proxy server for Application debugging, testing and development.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
*/
import { WebsocketApi } from './ws'

export interface IDashboardPlugin {
  name: string
  title: string
  initializeTab(): JQuery<HTMLElement>
  initializeHeader(): JQuery<HTMLElement>
  initializeBody(): JQuery<HTMLElement>
  activated(): void
  deactivated(): void
}

export interface IPluginConstructor {
  new (websocketApi: WebsocketApi): IDashboardPlugin
}

export abstract class DashboardPlugin implements IDashboardPlugin {
  protected websocketApi: WebsocketApi

  public constructor (websocketApi: WebsocketApi) {
    this.websocketApi = websocketApi
  }

  public makeTab (name: string, icon: string) : JQuery<HTMLElement> {
    return $('<a/>')
      .attr({
        href: '#',
        plugin_name: this.name
      })
      .addClass('nav-link')
      .text(name)
      .prepend(
        $('<i/>')
          .addClass('fa')
          .addClass('fa-fw')
          .addClass(icon)
      )
  }

  public makeHeader (title: string) : JQuery<HTMLElement> {
    return $('<div></div>')
      .addClass('container-fluid')
      .append(
        $('<div></div>')
          .addClass('row')
          .append(
            $('<div></div>')
              .addClass('col-6')
              .append(
                $('<p></p>')
                  .addClass('h3')
                  .text(title)
              )
          )
      )
  }

  public abstract readonly name: string
  public abstract readonly title: string
  public abstract initializeTab() : JQuery<HTMLElement>
  public abstract initializeHeader(): JQuery<HTMLElement>
  public abstract initializeBody(): JQuery<HTMLElement>
  public abstract activated(): void
  public abstract deactivated(): void
}
