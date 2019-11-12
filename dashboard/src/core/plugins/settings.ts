/*
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Programmable, TLS interception capable
    proxy server for Application debugging, testing and development.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
*/
import { DashboardPlugin } from '../plugin'

export class SettingsPlugin extends DashboardPlugin {
  public name: string = 'settings'

  public initializeTab () : JQuery<HTMLElement> {
    return this.makeTab('Settings', 'fa-clog')
  }

  public initializeSkeleton (): JQuery<HTMLElement> {
    return this.getAppHeader()
      .add(this.getAppBody())
  }

  public activated (): void {}

  public deactivated (): void {}

  private getAppHeader (): JQuery<HTMLElement> {
    return $('<div></div>')
      .addClass('app-header')
      .append(
        $('<div></div>')
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
                      .text('Settings')
                  )
              )
          )
      )
  }

  private getAppBody (): JQuery<HTMLElement> {
    return $('<div></div>')
      .addClass('app-body')
  }
}
