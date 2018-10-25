for i in range(2):
    try:
        print('try', i)
        raise Exception
        # print ('pass') #not work after exception
    except:
        print('except', i)
        # continue
    # finally:
    #     print('finally', i)
    print('keep going', i)

