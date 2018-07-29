from matplotlib.patches import Circle, Rectangle, Arc
import matplotlib.pyplot as plt
import numpy as np


def get_hex(value, max_val):
    """Get hex given a value and the maximum allowed value."""
    value = float(value)
    if value > 0:
        rgb = (225 + 25 * min((value / max_val), 1),
               225 - 70 * min((value / max_val), 1),
               225 - 225 * min((value / max_val), 1))
    else:
        rgb = (225 + 225 * max((value / max_val), -1),
               225 + 110 * max((value / max_val), -1),
               225 + 25 * max((value / max_val), -1))
    return '{}'.format('#%02x%02x%02x' % tuple(rgb))


def draw_court(values, max_value, ax=None, color='black', lw=2, outer_lines=False):
    """Adapted from http://savvastjortjoglou.com/nba-play-by-play-movements.html"""
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add Back Court
    ax.add_patch(
        Rectangle(
            (-250, -48),  # (x,y)
            500,  # width
            550,  # height
            facecolor=get_hex(values['Backcourt'], max_value)
        ))
    # Add 3 beyond arc
    ax.add_patch(
        Rectangle(
            (-250, -48),  # (x,y)
            500,  # width
            450,  # height
            facecolor=get_hex(values['Above the Break 3'], max_value)
        ))
    # Add Midrange
    ax.add_patch(
        Circle(
            (0, 0),  # (x,y)
            237,
            facecolor=get_hex(values['Mid-Range'], max_value)
        ))
    # Add right corner three
    ax.add_patch(
        Rectangle(
            (-250, -48),  # (x,y)
            30,  # width
            138,  # height
            facecolor=get_hex(values['Right Corner 3'], max_value)
        ))
    # Add left corner three
    ax.add_patch(
        Rectangle(
            (220, -48),  # (x,y)
            30,  # width
            138,  # height
            facecolor=get_hex(values['Left Corner 3'], max_value)
        ))
    # Add paint, non resticted area
    ax.add_patch(
        Rectangle(
            (-80, -48),  # (x,y)
            160,
            190,
            facecolor=get_hex(values['In The Paint (Non-RA)'], max_value)
        ))

    # Add Restricted Area
    ax.add_patch(
        Circle(
            (0, 0),  # (x,y)
            40,
            facecolor=get_hex(values['Restricted Area'], max_value)
        ))
    # Add background for legend
    ax.add_patch(
        Rectangle(
            (180, 300),  # (x,y)
            70,
            200,
            facecolor='white'
        ))
    # Add legend
    legend_values = np.linspace(-max_value, max_value, 9)

    for ind, val in enumerate(legend_values):
        ax.add_patch(
            Rectangle(
                (185, 305 + 20 * ind),  # (x,y)
                20,
                20,
                facecolor=get_hex(val, max_value)
            ))
        ax.text(225, 310 + 20 * ind, round(val, 2))
    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax
